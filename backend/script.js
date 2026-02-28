console.log("SCRIPT LOADED ✅");

// ===============================
// WAIT FOR DOM LOAD
// ===============================
document.addEventListener("DOMContentLoaded", function () {

const selfieInput = document.getElementById("selfieInput");
const selfiePreview = document.getElementById("selfiePreview");
const findBtn = document.getElementById("findBtn");
const gallery = document.getElementById("gallery");
const loadingText = document.getElementById("loadingText");

let currentImages = [];
let currentIndex = 0;


// ===============================
// STOP ANY FORM SUBMIT
// ===============================
document.addEventListener("submit", function(e){
    e.preventDefault();
    e.stopPropagation();
    return false;
});


// ===============================
// SELFIE PREVIEW
// ===============================
selfieInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) return;

    if (!file.type.startsWith("image/")) {

        alert("Only image files allowed");
        this.value = "";
        selfiePreview.style.display = "none";
        return;

    }

    const reader = new FileReader();

    reader.onload = function (e) {

        selfiePreview.src = e.target.result;
        selfiePreview.style.display = "block";

    };

    reader.readAsDataURL(file);

});


// ===============================
// FIND PHOTOS BUTTON
// ===============================
findBtn.addEventListener("click", async function (e) {

    e.preventDefault();
    e.stopPropagation();

    console.log("BUTTON CLICKED");

    const eventId = document.getElementById("eventId").value.trim();
    const selfieFile = selfieInput.files[0];

    if (!eventId) {
        alert("Please enter Event ID");
        return;
    }

    if (!selfieFile) {
        alert("Please upload your selfie first");
        return;
    }

    gallery.innerHTML = "";
    loadingText.innerText = "AI is analyzing your face...";

    try {

        const formData = new FormData();
        formData.append("selfie", selfieFile);

        const response = await fetch(
            `/match/${eventId}`,
            {
                method: "POST",
                body: formData
            }
        );

        const aiData = await response.json();

        console.log("AI RESULT:", aiData);

        loadingText.innerText = "";

        if (aiData.success && aiData.matched.length > 0) {

            currentImages = aiData.matched;

            aiData.matched.forEach((img, index) => {

                const imageElement = document.createElement("img");

                imageElement.src = img;
                imageElement.style.width = "100%";
                imageElement.style.borderRadius = "16px";
                imageElement.style.cursor = "pointer";
                imageElement.style.transition = "0.3s";

                imageElement.onmouseenter = () => {
                    imageElement.style.transform = "scale(1.03)";
                };

                imageElement.onmouseleave = () => {
                    imageElement.style.transform = "scale(1)";
                };

                imageElement.onclick = () => openFullscreen(index);

                gallery.appendChild(imageElement);

            });

        } else {

            gallery.innerHTML = "<p>No matching photos found</p>";

        }

    } catch (err) {

        console.error(err);

        loadingText.innerText = "";
        gallery.innerHTML = "<p>AI Server error</p>";

    }

});


// ===============================
// PREMIUM FULLSCREEN VIEW
// ===============================
function openFullscreen(index) {

    currentIndex = index;

    // OVERLAY
    const overlay = document.createElement("div");

    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.background = "rgba(0,0,0,0.96)";
    overlay.style.display = "flex";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";
    overlay.style.flexDirection = "column";
    overlay.style.zIndex = "9999";
    overlay.style.animation = "fadeIn 0.25s ease";


    // IMAGE
    const img = document.createElement("img");

    img.src = currentImages[currentIndex];
    img.style.maxWidth = "92%";
    img.style.maxHeight = "82%";
    img.style.borderRadius = "18px";
    img.style.boxShadow = "0 0 40px rgba(0,0,0,0.8)";
    img.style.marginBottom = "20px";


    // BUTTON CONTAINER
    const btnContainer = document.createElement("div");

    btnContainer.style.display = "flex";
    btnContainer.style.gap = "15px";


    // DOWNLOAD BUTTON (PREMIUM)
    const downloadBtn = document.createElement("a");

    downloadBtn.innerText = "⬇ Download";
    downloadBtn.href = currentImages[currentIndex];
    downloadBtn.download = "";

    downloadBtn.style.padding = "12px 22px";
    downloadBtn.style.borderRadius = "12px";
    downloadBtn.style.background = "linear-gradient(135deg,#00c6ff,#0072ff)";
    downloadBtn.style.color = "white";
    downloadBtn.style.fontWeight = "600";
    downloadBtn.style.textDecoration = "none";
    downloadBtn.style.boxShadow = "0 4px 18px rgba(0,114,255,0.5)";
    downloadBtn.style.transition = "0.3s";
    downloadBtn.style.cursor = "pointer";

    downloadBtn.onmouseenter = () => {
        downloadBtn.style.transform = "scale(1.08)";
    };

    downloadBtn.onmouseleave = () => {
        downloadBtn.style.transform = "scale(1)";
    };


    // CLOSE BUTTON (PREMIUM)
    const closeBtn = document.createElement("button");

    closeBtn.innerText = "✕ Close";

    closeBtn.style.padding = "12px 22px";
    closeBtn.style.borderRadius = "12px";
    closeBtn.style.border = "none";
    closeBtn.style.background = "linear-gradient(135deg,#ff416c,#ff4b2b)";
    closeBtn.style.color = "white";
    closeBtn.style.fontWeight = "600";
    closeBtn.style.boxShadow = "0 4px 18px rgba(255,75,43,0.5)";
    closeBtn.style.cursor = "pointer";
    closeBtn.style.transition = "0.3s";

    closeBtn.onmouseenter = () => {
        closeBtn.style.transform = "scale(1.08)";
    };

    closeBtn.onmouseleave = () => {
        closeBtn.style.transform = "scale(1)";
    };

    closeBtn.onclick = () => {
        document.body.removeChild(overlay);
    };


    // CLICK OUTSIDE TO CLOSE
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            document.body.removeChild(overlay);
        }
    };


    // APPEND
    btnContainer.appendChild(downloadBtn);
    btnContainer.appendChild(closeBtn);

    overlay.appendChild(img);
    overlay.appendChild(btnContainer);

    document.body.appendChild(overlay);

}

});