"use strict";

/*
 * Get DOM elements
 */

const headlineElement = document.querySelector(
  "#original-headline"
) as HTMLHeadingElement;

const rewriteForm = document.querySelector("#rewrite-form") as HTMLFormElement;
const rewriteFormInput = rewriteForm.querySelector("#text") as HTMLInputElement;
const rewriteDisplay = document.querySelector(
  "#rewrite-display"
) as HTMLParagraphElement;

/*
 * Event Listeners
 */

rewriteForm.addEventListener("submit", (evt) => {
  evt.preventDefault();
  rewriteFormHandler();
});

/*
 * Main Form Functions
 */

interface RewriteRequest {
  text: string;
  headline_id: string;
}

function rewriteFormHandler() {
  const requestBody: RewriteRequest = {
    text: rewriteFormInput.value,
    headline_id: headlineElement.dataset.id as string,
  };
  const rewrite = sendRewrite(requestBody);
  console.log("handler: ", rewrite);
  showRewrite(rewrite);
}

interface Rewrite {
  rewrite: {
    id: string;
    headline_id: string;
    user_id: string;
    text: string;
    timestamp: string;
    semantic_score: number;
    semantic_match: number;
    sentiment_score: number;
  };
}

function showRewrite(rewrite: Promise<Rewrite>): void {
  console.log("show: ", rewrite);
  rewrite.then(
    (r) =>
    (rewriteDisplay.innerText = `${r.rewrite.text} | Score: ${calculateScore(
      r.rewrite.semantic_match
    )}`)
  );
}

function calculateScore(match: number): number {
  return Math.round(Math.abs(match) * 100);
}

function sendRewrite(data: RewriteRequest) {
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
