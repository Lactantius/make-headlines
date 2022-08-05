"use strict";
/*
 * Get DOM elements
 */
const headlineElement = document.querySelector("#original-headline");
const rewriteForm = document.querySelector("#rewrite-form");
const rewriteFormText = rewriteForm.querySelector("input");
function rewriteFormHandler() {
    const requestBody = {
        text: rewriteFormText.value,
        headline_id: headlineElement.dataset.id,
    };
    return sendRewrite(requestBody);
}
function sendRewrite(data) {
    return fetch("/api/rewrites", { method: "POST", body: JSON.stringify(data) });
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
