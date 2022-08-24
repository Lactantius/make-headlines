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
  showHeadline(headlineElement);
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
  displayRewrite(rewrite, rewriteList);
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

interface Error {
  error: string;
}

function displayRewrite(
  rewrite: Promise<Rewrite | Error>,
  rewriteList: HTMLUListElement
): void {
  const li = document.createElement("li");

  rewrite.then((r) => (li.innerText = formatRewrite(r)));
  rewriteList.prepend(li);
  rewriteList.style.display = "block";
}

function formatRewrite(data: Rewrite | Error): string {
  if ("rewrite" in data) {
    return `${data.rewrite.text} | Score: ${calculateScore(
      data.rewrite.sentiment_match
    )}`;
  } else {
    return data.error;
  }
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

async function showHeadline(
  heading: HTMLHeadingElement,
  headlineData?: Headline
): Promise<void> {
  const headline = headlineData || (await getHeadline());
  heading.innerText = headline.text;
  heading.dataset.id = headline.id;
  (heading.parentElement as HTMLAnchorElement).setAttribute(
    "href",
    headline.url
  );

  const source = document.createElement("span");
  source.classList.add("headline-source");
  source.innerText = ` Source: ${headline.source} `;
  heading.append(source);

  affectP.innerText = calculateAffect(headline.sentiment_score);
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
  mainRewriteDisplay.style.display = "none";
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

  (
    document.querySelector("#previous-headlines") as HTMLHeadingElement
  ).style.display = "block";

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
 * Rewrites Page: Functions for getting and displaying all of a user's old rewrites
 */

interface Headline {
  id: string;
  text: string;
  sentiment_score: number;
  date: string;
  source_id: string;
  source: string;
  url: string;
  rewrites?: Rewrite[];
}

async function showOldRewrites(): Promise<void> {
  const hContainer = document.querySelector(
    "#previous-rewrites-container"
  ) as HTMLDivElement;
  const headlines: Headline[] = await fetch(
    "/api/users/logged_in_user/rewrites",
    {
      headers: { "Content-Type": "application/json" },
    }
  )
    .then((data) => data.json())
    .catch((err: Error) => showOldRewritesError(err));

  headlines.forEach((headline) => {
    const hElement = document.createElement("h2");
    showHeadline(hElement, headline);
    hContainer.append(hElement);
  });
}

function showOldRewritesError(err: Error): void {
  alert(err);
}

/*
 * Initialize
 */

function main(): void {
  const path = location.pathname;
  if (path === "/") {
    showHeadline(headlineElement);
  } else if (path === "/rewrites") {
    showOldRewrites();
  }
}

main();
