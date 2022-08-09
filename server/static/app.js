"use strict";
/*
 * Get DOM elements
 */
const headlineElement = document.querySelector("#original-headline");
const rewriteContainer = document.querySelector("#rewrite-container");
const rewriteForm = document.querySelector("#rewrite-form");
const rewriteFormInput = rewriteForm.querySelector("#text");
const rewriteDisplay = document.querySelector("#rewrite-list");
const switchHeadlineForm = document.querySelector("#switch-headline");
const oldRewrites = document.querySelector("#old-rewrites");
/*
 * Event Listeners
 */
rewriteForm.addEventListener("submit", (evt) => {
    evt.preventDefault();
    rewriteFormHandler();
});
switchHeadlineForm.addEventListener("submit", (evt) => {
    evt.preventDefault();
    replaceHeadline();
});
function rewriteFormHandler() {
    const requestBody = {
        text: rewriteFormInput.value,
        headline_id: headlineElement.dataset.id,
    };
    const rewrite = sendRewrite(requestBody);
    showRewrite(rewrite);
}
function showRewrite(rewrite) {
    const li = document.createElement("li");
    rewrite.then((r) => (li.innerText = `${r.rewrite.text} | Score: ${calculateScore(r.rewrite.sentiment_match)}`));
    rewriteDisplay.prepend(li);
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
function moveHeadline() {
    if (rewriteDisplay.children.length === 0) {
        return;
    }
    const oldHeadlineContainer = rewriteContainer.cloneNode(true);
    oldHeadlineContainer.setAttribute("id", "");
    oldRewrites.prepend(oldHeadlineContainer);
}
// .then(res => res.json().then(json => json.text))
/*
 * Initialize
 */
replaceHeadline();
