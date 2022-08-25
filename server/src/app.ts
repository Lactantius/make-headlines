"use strict";

main();

/*
 * Event Listeners
 */

function addIndexPageListeners(
  rewriteForm: HTMLFormElement,
  mainRewriteDisplay: HTMLUListElement,
  mainRewriteContainer: HTMLDivElement,
  rewriteFormInput: HTMLInputElement,
  mainHeadlineElement: HTMLHeadingElement,
  switchHeadlineForm: HTMLFormElement,
  mainSentimentPar: HTMLParagraphElement,
  mainHeadlineLink: HTMLAnchorElement,
  oldRewritesContainer: HTMLDivElement
): void {
  rewriteForm.addEventListener("submit", (evt) => {
    evt.preventDefault();
    rewriteFormHandler(
      mainRewriteDisplay,
      rewriteFormInput.value,
      mainHeadlineElement.dataset.id as string
    );
    rewriteForm.reset();
  });

  switchHeadlineForm.addEventListener("submit", (evt) => {
    evt.preventDefault();
    moveHeadline(
      mainRewriteDisplay,
      mainRewriteContainer,
      oldRewritesContainer
    );
    showHeadline(mainHeadlineElement, mainSentimentPar, mainHeadlineLink);
  });
}

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
): Promise<void> {
  const requestBody: RewriteRequest = {
    text: text,
    headline_id: headlineId,
  };
  const rewrite = await sendRewrite(requestBody);
  "error" in rewrite
    ? showLoginPrompt(rewrite.error, rewriteList)
    : showRewrite(rewrite, rewriteList);
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

interface ErrorResponse {
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

function sendRewrite(
  data: RewriteRequest
): Promise<RewriteResponse | ErrorResponse> {
  return fetch("/api/rewrites", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((p) => p.json())
    .then((data: RewriteResponse) => data)
    .catch((err: ErrorResponse) => err);
}

/*
 * Replace headlines
 */

async function showHeadline(
  heading: HTMLHeadingElement,
  sentimentPar: HTMLParagraphElement,
  container: HTMLAnchorElement,
  headlineData?: Headline
): Promise<void> {
  const headline = headlineData || (await getHeadline());
  heading.innerText = headline.text;
  heading.dataset.id = headline.id;
  container.setAttribute("href", headline.url);

  const source = document.createElement("span");
  source.classList.add("headline-source");
  source.innerText = ` Source: ${headline.source} `;
  heading.append(source);

  sentimentPar.innerText = calculateAffect(headline.sentiment_score);
  container.append(heading);
  container.append(sentimentPar);
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

function moveHeadline(
  mainRewriteDisplay: HTMLUListElement,
  mainRewriteContainer: HTMLDivElement,
  oldRewritesContainer: HTMLDivElement
) {
  if (mainRewriteDisplay.children.length === 0) {
    return;
  }
  //(rewriteContainer.querySelector("p") as HTMLParagraphElement).remove();
  const oldHeadline = mainRewriteContainer.cloneNode(true) as HTMLDivElement;
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

  oldRewritesContainer.prepend(oldHeadline);
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
  const allHeadlinesContainer = document.querySelector(
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

  allHeadlinesContainer.replaceChildren("");
  headlines.forEach((headline) => {
    const hContainer = document.createElement("div");
    hContainer.classList.add("rewrite-container");
    const link = document.createElement("a");
    const hElement = document.createElement("h2");
    const sentimentPar = document.createElement("p");
    showHeadline(hElement, sentimentPar, link, headline);
    hContainer.append(link);

    const rewrites = document.createElement("ul");
    (headline.rewrites as Rewrite[]).forEach((rewrite) => {
      showRewrite(rewrite, rewrites);
    });
    hContainer.append(rewrites);
    allHeadlinesContainer.append(hContainer);
  });
}

function showOldRewritesError(err: Error): void {
  alert(err);
}

/*
 * Notifications
 */

function showLoginPrompt(msg: string, rewriteList: HTMLUListElement): void {
  const body = document.querySelector("body") as HTMLBodyElement;
  const prompt = document.createElement("prompt");

  prompt.classList.add("modal");
  prompt.append(formatErrorMessage(msg));

  const closeButton = makeCloseButton(prompt);
  prompt.append(closeButton);

  body.append(prompt);
}

function formatErrorMessage(msg: string): HTMLSpanElement {
  const span = document.createElement("span");
  if (msg === "Please login before making additional requests.") {
    span.innerHTML =
      'Please&nbsp; <a href="/login">login</a> &nbsp;or&nbsp; <a href="/signup">sign up</a> &nbsp;before making additional requests.';
  } else {
    span.innerHTML = msg;
  }
  return span;
}

function makeCloseButton(parent: HTMLElement): HTMLButtonElement {
  console.log("Making button");
  const button = document.createElement("button");
  button.innerText = "X";
  button.classList.add("close-btn");
  button.addEventListener("click", (evt: MouseEvent) => {
    evt.preventDefault();
    parent.remove();
  });
  return button;
}

/*
 * Main
 */

function main(): void {
  const path = location.pathname;
  if (path === "/") {
    const mainHeadlineElement = document.querySelector(
      "#original-headline"
    ) as HTMLHeadingElement;

    const rewriteForm = document.querySelector(
      "#rewrite-form"
    ) as HTMLFormElement;

    const rewriteFormInput = rewriteForm.querySelector(
      "#text"
    ) as HTMLInputElement;

    const mainRewriteContainer = document.querySelector(
      "#main-rewrite-container"
    ) as HTMLDivElement;

    const mainRewriteDisplay = document.querySelector(
      "#rewrite-list"
    ) as HTMLUListElement;

    const switchHeadlineForm = document.querySelector(
      "#switch-headline"
    ) as HTMLFormElement;

    const mainHeadlineLink = mainRewriteContainer.querySelector(
      "a"
    ) as HTMLAnchorElement;

    const mainSentimentPar = mainRewriteContainer.querySelector(
      "p"
    ) as HTMLParagraphElement;

    const oldRewritesContainer = document.querySelector(
      "#old-rewrites"
    ) as HTMLDivElement;

    showHeadline(mainHeadlineElement, mainSentimentPar, mainHeadlineLink);
    addIndexPageListeners(
      rewriteForm,
      mainRewriteDisplay,
      mainRewriteContainer,
      rewriteFormInput,
      mainHeadlineElement,
      switchHeadlineForm,
      mainSentimentPar,
      mainHeadlineLink,
      oldRewritesContainer
    );
  } else if (path === "/rewrites") {
    showOldRewrites();
  }
}
