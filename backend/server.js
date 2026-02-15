const express = require("express");
const cors = require("cors");
const multer = require("multer");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 5000;

/* ===============================
   IMAGE FILE FILTER
=================================*/
const imageFilter = (req, file, cb) => {
  if (file.mimetype.startsWith("image/")) {
    cb(null, true);
  } else {
    cb(new Error("Only image files allowed"), false);
  }
};

/* ===============================
   EVENT PHOTO STORAGE
=================================*/
const eventStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    const eventId = req.params.eventId;
    const dir = path.join(__dirname, "uploads", "events", eventId);

    fs.mkdirSync(dir, { recursive: true });
    cb(null, dir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + "-" + file.originalname);
  }
});

const uploadEventPhotos = multer({
  storage: eventStorage,
  fileFilter: imageFilter
});

/* ===============================
   SELFIE STORAGE (SEPARATE)
=================================*/
const selfieStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    const eventId = req.params.eventId;
    const dir = path.join(__dirname, "uploads", "events", eventId, "selfies");

    fs.mkdirSync(dir, { recursive: true });
    cb(null, dir);
  },
  filename: (req, file, cb) => {
    cb(null, "selfie-" + Date.now() + path.extname(file.originalname));
  }
});

const uploadSelfie = multer({
  storage: selfieStorage,
  fileFilter: imageFilter
});

/* ===============================
   TEST ROUTE
=================================*/
app.get("/", (req, res) => {
  res.send("🚀 PICARO backend running");
});

/* ===============================
   UPLOAD EVENT PHOTOS
=================================*/
app.post("/upload/:eventId", uploadEventPhotos.array("photos"), (req, res) => {
  res.json({
    success: true,
    eventId: req.params.eventId,
    files: req.files.map(file => file.filename)
  });
});

/* ===============================
   UPLOAD SELFIE (CLIENT)
=================================*/
app.post("/upload-selfie/:eventId", uploadSelfie.single("selfie"), (req, res) => {
  res.json({
    success: true,
    message: "Selfie uploaded successfully",
    file: req.file.filename
  });
});

/* ===============================
   GET EVENT IMAGES
=================================*/
app.get("/events/:eventId/images", (req, res) => {
  const eventId = req.params.eventId;
  const eventPath = path.join(__dirname, "uploads", "events", eventId);

  if (!fs.existsSync(eventPath)) {
    return res.status(404).json({
      success: false,
      message: "Event not found"
    });
  }

  const images = fs.readdirSync(eventPath).filter(file => {
    return !fs.statSync(path.join(eventPath, file)).isDirectory();
  });

  const imageUrls = images.map(img =>
    `http://localhost:${PORT}/events/${eventId}/${img}`
  );

  res.json({
    success: true,
    eventId,
    images: imageUrls
  });
});

/* ===============================
   GET ALL EVENTS
=================================*/
app.get("/events", (req, res) => {
  const eventsDir = path.join(__dirname, "uploads", "events");

  if (!fs.existsSync(eventsDir)) {
    return res.json({ success: true, events: [] });
  }

  const eventFolders = fs.readdirSync(eventsDir).filter(folder =>
    fs.statSync(path.join(eventsDir, folder)).isDirectory()
  );

  const eventsData = eventFolders.map(eventId => {
    const eventPath = path.join(eventsDir, eventId);

    const images = fs.readdirSync(eventPath).filter(file => {
      return !fs.statSync(path.join(eventPath, file)).isDirectory();
    });

    return {
      eventId,
      totalPhotos: images.length,
      coverPhoto:
        images.length > 0
          ? `http://localhost:${PORT}/events/${eventId}/${images[0]}`
          : null
    };
  });

  res.json({
    success: true,
    events: eventsData
  });
});

/* ===============================
   DELETE EVENT
=================================*/
app.delete("/events/:eventId", (req, res) => {
  const eventId = req.params.eventId;
  const eventPath = path.join(__dirname, "uploads", "events", eventId);

  if (!fs.existsSync(eventPath)) {
    return res.status(404).json({
      success: false,
      message: "Event not found"
    });
  }

  try {
    fs.rmSync(eventPath, { recursive: true, force: true });

    res.json({
      success: true,
      message: "Event deleted successfully"
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Error deleting event"
    });
  }
});

/* ===============================
   STATIC IMAGES
=================================*/
app.use(
  "/events",
  express.static(path.join(__dirname, "uploads", "events"))
);

/* ===============================
   START SERVER
=================================*/
app.listen(PORT, () => {
  console.log(`✅ PICARO server running on port ${PORT}`);
});