"use strict";

/*
 * Get DOM elements
 */

const headlineElement = document.querySelector(
  "#original-headline"
) as HTMLHeadingElement;

const rewriteForm = document.querySelector("#rewrite-form") as HTMLFormElement;
const rewriteFormText = rewriteForm.querySelector("input") as HTMLInputElement;

/*
 * Main Form Functions
 */

interface RewriteRequest {
  text: string;
  headline_id: string;
}

function rewriteFormHandler() {
  const requestBody: RewriteRequest = {
    text: rewriteFormText.value,
    headline_id: headlineElement.dataset.id as string,
  };
  return sendRewrite(requestBody);
}

function sendRewrite(data: RewriteRequest) {
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
