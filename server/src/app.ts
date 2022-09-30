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
  mainHeadlineLink: HTMLAnchorElement,
  oldRewritesContainer: HTMLDivElement
): void {
  rewriteForm.addEventListener("submit", (evt) => {
    evt.preventDefault();
    void rewriteFormHandler(
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
    void showHeadline(mainHeadlineElement, mainHeadlineLink);
  });
}

/*
 * Interfaces
 */

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

interface RewriteReq {
  text: string;
  headline_id: string;
}

interface RewriteRes {
  rewrite: Rewrite;
}

interface ErrorRes {
  error: string;
}

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

interface HeadlineRes {
  headline: Headline;
}

/*
 * Main Form Functions
 */

/* Runs when main form is submitted */
async function rewriteFormHandler(
  rewriteList: HTMLUListElement,
  text: string,
  headlineId: string
): Promise<void> {
  const requestBody: RewriteReq = {
    text: text,
    headline_id: headlineId,
  };
  const rewrite = await sendRewrite(requestBody);
  "error" in rewrite
    ? showError(rewrite.error)
    : showRewrite(rewrite.rewrite, rewriteList);
}

/* Add rewrite to DOM */
function showRewrite(rewrite: Rewrite, container: HTMLUListElement): void {
  const rewriteDiv = document.createElement("div");
  rewriteDiv.classList.add("rewrite-div");

  const heading = document.createElement("h2");
  heading.innerText = rewrite.text;
  heading.dataset.id = rewrite.id;

  const deleteButton = makeDeleteButton(rewrite.id, rewriteDiv);

  rewriteDiv.append(deleteButton);
  rewriteDiv.append(heading);
  rewriteDiv.append(makeSentimentGraph(rewrite.sentiment_score));
  rewriteDiv.append(makeDifferenceGraph(rewrite.sentiment_match));
  container.style.display = "block";
  container.prepend(rewriteDiv);
}

/* Delete button for headline rewrites */
function makeDeleteButton(
  id: string,
  rewriteContainer: HTMLDivElement
): HTMLButtonElement {
  const button = document.createElement("button");
  button.innerText = "X";
  button.classList.add("delete-btn");
  button.addEventListener("click", (evt: MouseEvent) => {
    evt.preventDefault();
    void fetch(`/api/rewrites/${id}`, { method: "DELETE" });
    /* Hide list of rewrites if this is the last one */
    if (rewriteContainer.parentElement!.childElementCount === 1) {
      rewriteContainer.parentElement!.style.display = "none";
    }
    rewriteContainer.remove();
  });
  return button;
}

function calculateScore(match: number): number {
  return Math.round(Math.abs(match) * 100);
}

/* Graph shown under rewrites */
function makeDifferenceGraph(match: number): HTMLDivElement {
  const graph = document.createElement("div");
  graph.classList.add("difference-graph");

  const diff = calculateScore(match);

  const text = document.createElement("span");
  text.innerText = `Difference: ${diff}`;

  const bar = document.createElement("div");
  bar.setAttribute("style", `width: ${diff / 2}%`);

  graph.append(text);
  graph.append(bar);
  return graph;
}

/* API Request to get sentiment analysis */
function sendRewrite(data: RewriteReq): Promise<RewriteRes | ErrorRes> {
  return fetch("/api/rewrites", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((p) => p.json())
    .then((data: RewriteRes) => data)
    .catch((err: ErrorRes) => err);
}

/*
 * Replace headlines
 */

/* Add headline to DOM */
async function showHeadline(
  heading: HTMLHeadingElement,
  container: HTMLAnchorElement,
  headlineData?: Headline
): Promise<void> {
  const headline = headlineData ?? (await getHeadline());
  console.log(headline);
  "error" in headline
    ? showError(headline.error)
    : ((headline: Headline) => {
      heading.innerText = headline.text;
      heading.dataset.id = headline.id;
      container.setAttribute("href", headline.url);

      const sentimentGraph = container.querySelector(".sentiment-graph");
      if (sentimentGraph) {
        sentimentGraph.remove();
      }

      const source = document.createElement("span");
      source.classList.add("headline-source");
      source.innerText = ` Source: ${headline.source} `;
      heading.append(source);

      container.append(heading);
      container.append(makeSentimentGraph(headline.sentiment_score));
    })(headline);
}

/* Generates a graph of the sentiment score */
function makeSentimentGraph(sentiment: number): HTMLDivElement {
  const rounded = Math.round(sentiment * 100);
  const graph = document.createElement("div");
  graph.classList.add("sentiment-graph");

  const negative = document.createElement("div");
  negative.classList.add("sentiment-bar", "negative-sentiment-bar");

  const positive = document.createElement("div");
  positive.classList.add("sentiment-bar", "positive-sentiment-bar");

  const midpoint = document.createElement("span");
  midpoint.innerText = "-";

  const text = document.createElement("span");

  if (rounded < 0) {
    text.innerText = `Negative (${String(rounded * -1)}% certainty)`;
    text.classList.add("negative-text");
    negative.classList.add("active-bar");
    negative.setAttribute("style", `width: ${rounded * -1}%`);
  } else if (rounded > 0) {
    text.innerText = `Positive (${String(rounded)}% certainty)`;
    text.classList.add("positive-text");
    positive.classList.add("active-bar");
    positive.setAttribute("style", `width: ${rounded}%`);
  }

  graph.append(text);

  graph.append(negative);
  graph.append(midpoint);
  graph.append(positive);

  return graph;
}

/* API request for a headline */
function getHeadline(): Promise<Headline | ErrorRes> {
  return fetch("/api/headlines/random")
    .then((res) => res.json())
    .then((data: HeadlineRes) => data.headline)
    .catch((err: ErrorRes) => err);
}

/* Move the headline beneath the main form (for when the user wants to switch the headline) */
function moveHeadline(
  mainRewriteDisplay: HTMLUListElement,
  mainRewriteContainer: HTMLDivElement,
  oldRewritesContainer: HTMLDivElement
): void {
  if (mainRewriteDisplay.children.length === 0) {
    return;
  }
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
    void rewriteFormHandler(ul, input.value, headline.dataset.id as string);
    form.reset();
  });

  (
    document.querySelector("#previous-headlines") as HTMLHeadingElement
  ).style.display = "block";

  oldRewritesContainer.prepend(oldHeadline);
}

/* The main headline DIV has IDs used for event handling, so they are removed when the headline is switched */
function removeIds(node: Element): void {
  node.removeAttribute("id");
  const children = node.querySelectorAll("*");
  for (const child of children) {
    child.removeAttribute("id");
  }
}

/*
 * Rewrites Page: Functions for getting and displaying all of a user's old rewrites
 */

/* Get all the user's old rewrites and add them to the DOM */
async function showOldRewrites(): Promise<void> {
  const allHeadlinesContainer = document.querySelector(
    "#previous-rewrites-container"
  ) as HTMLDivElement;
  const headlines = await fetch("/api/users/logged_in_user/rewrites", {
    headers: { "Content-Type": "application/json" },
  })
    .then((data) => data.json())
    .then((lines: Headline[]) => lines)
    .catch((err: ErrorRes) => showError(err.error));

  if (headlines) {
    allHeadlinesContainer.replaceChildren("");
    headlines.forEach((headline) => {
      const hContainer = document.createElement("div");
      hContainer.classList.add("rewrite-container");
      const link = document.createElement("a");
      const hElement = document.createElement("h2");
      void showHeadline(hElement, link, headline);
      hContainer.append(link);

      const rewritesList = document.createElement("ul");
      (headline.rewrites as Rewrite[]).forEach((rewrite) => {
        showRewrite(rewrite, rewritesList);
      });
      hContainer.append(rewritesList);
      allHeadlinesContainer.append(hContainer);
    });
  }
}

/*
 * Notifications
 */

/* Makes a div with error messages */
function showError(msg: string): void {
  const body = document.querySelector("body") as HTMLBodyElement;
  const prompt = document.createElement("prompt");

  prompt.classList.add("modal");
  prompt.append(formatErrorMessage(msg));

  const closeButton = makeCloseButton(prompt);
  prompt.append(closeButton);

  body.append(prompt);
}

/* Rewrite some of the server's errors */
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

/* To remove the error div */
function makeCloseButton(parent: HTMLElement): HTMLButtonElement {
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

function setupIndexPage(): void {
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

  const oldRewritesContainer = document.querySelector(
    "#old-rewrites"
  ) as HTMLDivElement;

  (rewriteForm.querySelector("#text") as HTMLInputElement).focus();

  void showHeadline(mainHeadlineElement, mainHeadlineLink);
  addIndexPageListeners(
    rewriteForm,
    mainRewriteDisplay,
    mainRewriteContainer,
    rewriteFormInput,
    mainHeadlineElement,
    switchHeadlineForm,
    mainHeadlineLink,
    oldRewritesContainer
  );
}

function main(): void {
  const path = location.pathname;
  if (path === "/") {
    setupIndexPage();
  } else if (path === "/rewrites") {
    void showOldRewrites();
  }
}
