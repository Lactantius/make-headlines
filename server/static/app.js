"use strict";
/*
 * Get DOM elements
 */
const headlineElement = document.querySelector("#original-headline");
const rewriteContainer = document.querySelector("#main-rewrite-container");
const rewriteForm = document.querySelector("#rewrite-form");
const rewriteFormInput = rewriteForm.querySelector("#text");
const mainRewriteDisplay = document.querySelector("#rewrite-list");
const switchHeadlineForm = document.querySelector("#switch-headline");
const oldRewrites = document.querySelector("#old-rewrites");
/*
 * Event Listeners
 */
rewriteForm.addEventListener("submit", (evt) => {
    evt.preventDefault();
    rewriteFormHandler(mainRewriteDisplay, rewriteFormInput.value, headlineElement.dataset.id);
    rewriteForm.reset();
});
switchHeadlineForm.addEventListener("submit", (evt) => {
    evt.preventDefault();
    moveHeadline();
    replaceHeadline();
});
function rewriteFormHandler(rewriteList, text, headlineId) {
    const requestBody = {
        text: text,
        headline_id: headlineId,
    };
    const rewrite = sendRewrite(requestBody);
    showRewrite(rewrite, rewriteList);
}
function showRewrite(rewrite, rewriteList) {
    const li = document.createElement("li");
    rewrite.then((r) => (li.innerText = `${r.rewrite.text} | Score: ${calculateScore(r.rewrite.sentiment_match)}`));
    rewriteList.prepend(li);
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
    if (mainRewriteDisplay.children.length === 0) {
        return;
    }
    const oldHeadline = rewriteContainer.cloneNode(true);
    mainRewriteDisplay.replaceChildren("");
    /* Remove button to switch the headline */
    oldHeadline.querySelector("#switch-headline").remove();
    removeIds(oldHeadline);
    const ul = oldHeadline.querySelector("ul");
    const input = oldHeadline.querySelector("input[type=text]");
    const headline = oldHeadline.querySelector("h2");
    const form = oldHeadline.querySelector("form");
    form.addEventListener("submit", (evt) => {
        evt.preventDefault();
        rewriteFormHandler(ul, input.value, headline.dataset.id);
        form.reset();
    });
    oldRewrites.prepend(oldHeadline);
}
function removeIds(node) {
    node.removeAttribute("id");
    const children = node.querySelectorAll("*");
    for (let child of children) {
        child.removeAttribute("id");
    }
}
/*
 * Initialize
 */
replaceHeadline();
