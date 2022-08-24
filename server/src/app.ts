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

const mainSentimentPar = rewriteContainer.querySelector(
  "p"
) as HTMLParagraphElement;
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
  showHeadline(headlineElement, mainSentimentPar);
});

/*
 * Main Form Functions
 */

interface RewriteRequest {
  text: string;
  headline_id: string;
}

async function rewriteFormHandler(
  rewriteList: HTMLUListElement,
  text: string,
  headlineId: string
) {
  const requestBody: RewriteRequest = {
    text: text,
    headline_id: headlineId,
  };
  const rewrite: Rewrite = await sendRewrite(requestBody);
  showRewrite(rewrite, rewriteList);
}

interface RewriteResponse {
  rewrite: Rewrite;
}

interface Rewrite {
  id: string;
  headline_id: string;
  user_id: string;
  text: string;
  timestamp: string;
  semantic_score: number;
  sentiment_match: number;
  semantic_match: number;
  sentiment_score: number;
}

interface Error {
  error: string;
}

function showRewrite(
  rewrite: Rewrite | RewriteResponse,
  rewriteList: HTMLUListElement
): void {
  const li = document.createElement("li");

  li.innerText =
    "rewrite" in rewrite
      ? formatRewrite(rewrite.rewrite)
      : formatRewrite(rewrite);
  rewriteList.prepend(li);
  rewriteList.style.display = "block";
}

function formatRewrite(data: Rewrite): string {
  return `${data.text} | Score: ${calculateScore(data.sentiment_match)}`;
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
  sentimentPar: HTMLParagraphElement,
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

  sentimentPar.innerText = calculateAffect(headline.sentiment_score);
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
    const link = document.createElement("a");
    const hElement = document.createElement("h2");
    const sentimentPar = document.createElement("p");
    link.append(hElement);
    showHeadline(hElement, sentimentPar, headline);
    hContainer.append(hElement);

    const rewrites = document.createElement("ul");
    (headline.rewrites as Rewrite[]).forEach((rewrite) => {
      showRewrite(rewrite, rewrites);
    });
    hContainer.append(rewrites);
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
    showHeadline(headlineElement, mainSentimentPar);
  } else if (path === "/rewrites") {
    showOldRewrites();
  }
}

main();
