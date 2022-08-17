"use strict";

/*
 * Get DOM elements
 */

const headlineElement = document.querySelector(
  "#original-headline"
) as HTMLHeadingElement;

const rewriteContainer = document.querySelector(
  "#main-rewrite-container"
) as HTMLDivElement;
const rewriteForm = document.querySelector("#rewrite-form") as HTMLFormElement;
const rewriteFormInput = rewriteForm.querySelector("#text") as HTMLInputElement;
const mainRewriteDisplay = document.querySelector(
  "#rewrite-list"
) as HTMLUListElement;

const affectP = rewriteContainer.querySelector("p") as HTMLParagraphElement;
const switchHeadlineForm = document.querySelector(
  "#switch-headline"
) as HTMLFormElement;

const oldRewrites = document.querySelector("#old-rewrites") as HTMLDivElement;

/*
 * Event Listeners
 */

rewriteForm.addEventListener("submit", (evt) => {
  evt.preventDefault();
  rewriteFormHandler(
    mainRewriteDisplay,
    rewriteFormInput.value,
    headlineElement.dataset.id as string
  );
  rewriteForm.reset();
});

switchHeadlineForm.addEventListener("submit", (evt) => {
  evt.preventDefault();
  moveHeadline();
  replaceHeadline();
});

/*
 * Main Form Functions
 */

interface RewriteRequest {
  text: string;
  headline_id: string;
}

function rewriteFormHandler(
  rewriteList: HTMLUListElement,
  text: string,
  headlineId: string
) {
  const requestBody: RewriteRequest = {
    text: text,
    headline_id: headlineId,
  };
  const rewrite: Promise<Rewrite> = sendRewrite(requestBody);
  showRewrite(rewrite, rewriteList);
}

interface Rewrite {
  rewrite: {
    id: string;
    headline_id: string;
    user_id: string;
    text: string;
    timestamp: string;
    semantic_score: number;
    sentiment_match: number;
    semantic_match: number;
    sentiment_score: number;
  };
}

function showRewrite(
  rewrite: Promise<Rewrite>,
  rewriteList: HTMLUListElement
): void {
  const li = document.createElement("li");

  rewrite.then(
    (r) =>
    (li.innerText = `${r.rewrite.text} | Score: ${calculateScore(
      r.rewrite.sentiment_match
    )}`)
  );
  rewriteList.prepend(li);
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
    const parentAnchor = headlineElement.parentElement as HTMLAnchorElement;
    headlineElement.innerText = headline.text;
    headlineElement.dataset.id = headline.id;
    (headlineElement.parentElement as HTMLAnchorElement).setAttribute(
      "href",
      headline.url
    );

    const source = document.createElement("span");
    source.classList.add("headline-source");
    source.innerText = ` Source: ${headline.source}`;
    headlineElement.append(source);

    // const affect = document.createElement("p");
    // affect.classList.add("headline-affect");
    // affect.innerText = calculateAffect(headline.sentiment_score);
    // parentAnchor.append(affect);
    affectP.innerText = calculateAffect(headline.sentiment_score);
  });
}

function calculateAffect(score: number): string {
  const rounded = Math.round(score * 100);
  if (rounded < 0) {
    return `Negative (${rounded * -1}% certainty)`;
  } else if (rounded > 0) {
    return `Positive (${rounded}% certainty)`;
  } else {
    return "Neutral";
  }
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
  //(rewriteContainer.querySelector("p") as HTMLParagraphElement).remove();
  const oldHeadline = rewriteContainer.cloneNode(true) as HTMLDivElement;
  mainRewriteDisplay.replaceChildren("");
  /* Remove button to switch the headline */
  (oldHeadline.querySelector("#switch-headline") as HTMLFormElement).remove();

  removeIds(oldHeadline);

  const ul = oldHeadline.querySelector("ul") as HTMLUListElement;
  const input = oldHeadline.querySelector(
    "input[type=text]"
  ) as HTMLInputElement;
  const headline = oldHeadline.querySelector("h2") as HTMLHeadingElement;
  const form = oldHeadline.querySelector("form") as HTMLFormElement;

  form.addEventListener("submit", (evt) => {
    evt.preventDefault();
    rewriteFormHandler(ul, input.value, headline.dataset.id as string);
    form.reset();
  });
  oldRewrites.prepend(oldHeadline);
}

function removeIds(node: Element): void {
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
