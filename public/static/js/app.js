let currentFile = null;
let outputFile = null;

const imageInput = document.getElementById("imageInput");
const method = document.getElementById("method");
const threshold = document.getElementById("threshold");
const thresholdValue = document.getElementById("thresholdValue");
const blockSize = document.getElementById("blockSize");
const blockSizeValue = document.getElementById("blockSizeValue");
const cValue = document.getElementById("cValue");
const cText = document.getElementById("cText");
const adaptiveMethod = document.getElementById("adaptiveMethod");
const processBtn = document.getElementById("processBtn");
const downloadBtn = document.getElementById("downloadBtn");
const originalImage = document.getElementById("originalImage");
const resultImage = document.getElementById("resultImage");
const originalEmpty = document.getElementById("originalEmpty");
const resultEmpty = document.getElementById("resultEmpty");
const message = document.getElementById("message");
const otsuValue = document.getElementById("otsuValue");
const resultThreshold = document.getElementById("resultThreshold");
const blackPct = document.getElementById("blackPct");
const whitePct = document.getElementById("whitePct");
const processTime = document.getElementById("processTime");
const globalPanel = document.getElementById("globalPanel");
const otsuPanel = document.getElementById("otsuPanel");
const adaptivePanel = document.getElementById("adaptivePanel");

function showMessage(text, type = "info") {
    message.innerHTML = `
        <div class="alert alert-${type}">
            ${text}
        </div>
    `;
}

const updatePanels = () => {
    globalPanel.classList.add("d-none");
    otsuPanel.classList.add("d-none");
    adaptivePanel.classList.add("d-none");

    if (method.value === "global") {
        globalPanel.classList.remove("d-none");
    }
    if (method.value === "otsu") {
        otsuPanel.classList.remove("d-none");
    }
    if (method.value === "adaptive") {
        adaptivePanel.classList.remove("d-none");
    }
}
method.addEventListener("change", updatePanels);

threshold.addEventListener("input", () => {
    thresholdValue.textContent = threshold.value;
});

blockSize.addEventListener("input", () => {
    blockSizeValue.textContent = blockSize.value;
});

cValue.addEventListener("input", () => {
    cText.textContent = cValue.value;
});

const uploadImage = async () => {
    const file = imageInput.files[0];
    if (!file) {
        return;
    }

    const formData = new FormData();
    formData.append(
        "avatar",
        file
    );

    showMessage(
        "Đang upload ảnh...",
        "info"
    );

    try {
        const response = await fetch(
            "/upload",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();
        if (!data.success) {
            showMessage(
                data.message,
                "danger"
            );
            return;
        }
        currentFile = data.file;
        originalImage.src = `public/image/${data.file}`;
        originalImage.classList.remove("d-none");
        originalEmpty.classList.add("d-none");
        processBtn.disabled = false;

        resultImage.classList.add("d-none");
        resultEmpty.classList.remove("d-none");

        drawHistogram(data.histogram);

        showMessage(
            `Upload thành công: ${data.width} × ${data.height}`,
            "success"
        );
    } catch (error) {
        showMessage(
            `Có lỗi khi upload ảnh: ${error}`,
            "danger"
        );
    }
}

const processImage = async () => {
    if (!currentFile) {
        return;
    }

    processBtn.disabled = true;
    showMessage(
        "Đang xử lý...",
        "info"
    );

    const data = {
        file: currentFile,
        method: method.value,
        threshold: Number(threshold.value),
        block_size: Number(blockSize.value),
        c: Number(cValue.value),
        adaptive_method: adaptiveMethod.value
    };

    try {
        const response = await fetch(
            "/process",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify(data)
            }
        );

        const result = await response.json();
        if (!result.success) {
            showMessage(
                result.message,
                "danger"
            );
            return;
        }

        outputFile = result.output;
        resultImage.src = `/outputs/${result.output}?t=${Date.now()}`;
        resultImage.classList.remove("d-none");
        resultEmpty.classList.add("d-none");

        resultThreshold.textContent = result.threshold === null ? "Local" : result.threshold;
        otsuValue.textContent = result.threshold ?? "--";
        blackPct.textContent = result.stats.black_pct + "%";
        whitePct.textContent = result.stats.white_pct + "%";
        processTime.textContent = result.time + " ms";
        downloadBtn.disabled = false;

        showMessage(
            "Xử lý thành công.",
            "success"
        );
    } catch (error) {
        showMessage(
            "Có lỗi khi xử lý ảnh.",
            "danger"
        );
    } finally {
        processBtn.disabled = false;
    }
}

imageInput.addEventListener("change", uploadImage);
processBtn.addEventListener("click", processImage);

downloadBtn.addEventListener("click", () => {
    if (!outputFile) {
        return;
    }
    const link = document.createElement("a");
    link.href = `/outputs/${outputFile}`;
    link.download = "threshold_result.png";
    link.click();
}
);

const drawHistogram = (hist) => {
    const canvas = document.getElementById("histogram");
    const ctx = canvas.getContext("2d");

    const width = canvas.width = canvas.clientWidth * devicePixelRatio;
    const height = canvas.height = 150 * devicePixelRatio;

    ctx.clearRect(0, 0, width, height);
    const max = Math.max(...hist);
    const barWidth = width / 256;

    for (let i = 0; i < 256; i++) {
        const h = (hist[i] / max) * height;

        ctx.fillRect(
            i * barWidth,
            height - h,
            barWidth,
            h
        );
    }
}

updatePanels();