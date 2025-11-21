const btn = document.getElementById("generateBtn");
const input = document.getElementById("promptInput");
const loader = document.getElementById("loading");
const book = document.getElementById("comicBook");

btn.addEventListener("click", async () => {
    const prompt = input.value.trim();
    if (!prompt) return alert("Enter a story idea!");

    loader.classList.remove("hidden");
    book.classList.add("hidden");

    const res = await fetch("/api/story", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
    });

    const data = await res.json();
    const story = data.story;
    const images = data.images;
    const judge = data.judge;

    // Split story into two halves
    const paragraphs = story.split("\n").filter(line => line.trim() !== "");
    const half = Math.ceil(paragraphs.length / 2);

    document.getElementById("textPanel1").innerText = paragraphs
        .slice(0, half)
        .join("\n\n");

    document.getElementById("textPanel2").innerText = paragraphs
        .slice(half)
        .join("\n\n");

    // IMAGES (supports URL + base64)
    document.getElementById("imgPanel1").style.backgroundImage = `url("${images[0]}")`;
    document.getElementById("imgPanel2").style.backgroundImage = `url("${images[1]}")`;

    // JUDGE REVIEW
    document.getElementById("judgeText").innerText = judge;

    loader.classList.add("hidden");
    book.classList.remove("hidden");
});
