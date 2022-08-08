"use strict";
/*
 * Get DOM elements
 */
const headlineElement = document.querySelector("#original-headline");
const rewriteForm = document.querySelector("#rewrite-form");
const rewriteFormInput = rewriteForm.querySelector("#text");
const rewriteDisplay = document.querySelector("#rewrite-display");
/*
 * Event Listeners
 */
rewriteForm.addEventListener("submit", (evt) => {
    evt.preventDefault();
    rewriteFormHandler();
});
function rewriteFormHandler() {
    const requestBody = {
        text: rewriteFormInput.value,
        headline_id: headlineElement.dataset.id,
    };
    const rewrite = sendRewrite(requestBody);
    console.log("handler: ", rewrite);
    showRewrite(rewrite);
}
function showRewrite(rewrite) {
    console.log("show: ", rewrite);
    rewrite.then((r) => (rewriteDisplay.innerText = `${r.rewrite.text} | Score: ${calculateScore(r.rewrite.semantic_match)}`));
}
function calculateScore(match) {
    return Math.round(Math.abs(match) * 100);
}
function sendRewrite(data) {
    console.log(data);
    return fetch("/api/rewrites", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    })
        .then((p) => p.json())
        .then((data) => data)
        .catch((err) => err);
}
/*
 * Replace headlines
 */
function replaceHeadline() {
    getHeadline().then((headline) => {
        headlineElement.innerText = headline.text;
        headlineElement.dataset.id = headline.id;
    });
}
function getHeadline() {
    return fetch("/api/headlines/random")
        .then((res) => res.json())
        .then((data) => data.headline)
        .catch((err) => err);
}
// .then(res => res.json().then(json => json.text))
/*
 * Initialize
 */
replaceHeadline();
