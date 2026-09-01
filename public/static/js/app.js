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
    formData.append("avatar", file);

    showMessage("Đang upload ảnh...", "info");

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
            showMessage(data.message, "danger");
            return;
        }
        currentFile = data.file;
        originalImage.src = `/image/${data.file}`;
        originalImage.classList.remove("d-none");
        originalEmpty.classList.add("d-none");
        processBtn.disabled = false;

        resultImage.classList.add("d-none");
        resultEmpty.classList.remove("d-none");

        drawHistogram(data.histogram);

        showMessage(
            `Upload ảnh thành công:<br/>Kích thước: ${data.width}px × ${data.height}px`,
            "success"
        );
    } catch (error) {
        showMessage(`Có lỗi khi upload ảnh: ${error}`, "danger");
    }
}

const processImage = async () => {
    if (!currentFile) {
        return;
    }

    processBtn.disabled = true;
    showMessage("Đang xử lý...", "info");

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
            showMessage(result.message, "danger");
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

        showMessage("Xử lý thành công.", "success");
    } catch (error) {
        showMessage("Có lỗi khi xử lý ảnh.", "danger");
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
});

const drawHistogram = (hist) => {
    const canvas = document.getElementById("histogram");
    const ctx = canvas.getContext("2d");

    const dpr = window.devicePixelRatio || 1;
    const width = canvas.clientWidth;
    const height = 250;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, width, height);

    const paddingLeft = 55;
    const paddingRight = 20;
    const paddingTop = 20;
    const paddingBottom = 40;

    const graphWidth = width - paddingLeft - paddingRight;
    const graphHeight = height - paddingTop - paddingBottom;
    const max = Math.max(...hist);
    const barWidth = graphWidth / 256;

    ctx.fillStyle = "blue";
    for (let i = 0; i < 256; i++) {
        const barHeight = (hist[i] / max) * graphHeight;

        ctx.fillRect(
            paddingLeft + i * barWidth,
            paddingTop + graphHeight - barHeight,
            barWidth,
            barHeight
        );
    }

    ctx.strokeStyle = "black";
    ctx.lineWidth = 1;
    ctx.beginPath();
    // trục Y
    ctx.moveTo(paddingLeft, paddingTop);
    ctx.lineTo(paddingLeft, paddingTop + graphHeight);
    // trục X
    ctx.moveTo(paddingLeft, paddingTop + graphHeight);
    ctx.lineTo(paddingLeft + graphWidth, paddingTop + graphHeight);

    ctx.stroke();
    const xTicks = [0, 42, 85, 128, 170, 213, 255];

    ctx.fillStyle = "black";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";

    xTicks.forEach(value => {
        const x = paddingLeft + (value / 255) * graphWidth;
        ctx.beginPath();
        ctx.moveTo(x, paddingTop + graphHeight);
        ctx.lineTo(x, paddingTop + graphHeight + 5);

        ctx.stroke();
        ctx.fillText(value, x, paddingTop + graphHeight + 10);
    });

    const yTickCount = 5;
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";

    for (let i = 0; i < yTickCount; i++) {
        const value = (max / (yTickCount - 1)) * i;
        const y = paddingTop + graphHeight - (value / max) * graphHeight;

        ctx.beginPath();
        ctx.moveTo(paddingLeft - 5, y);
        ctx.lineTo(paddingLeft, y);

        ctx.stroke();
        ctx.fillText(Math.round(value), paddingLeft - 8, y);
    }
};

updatePanels();