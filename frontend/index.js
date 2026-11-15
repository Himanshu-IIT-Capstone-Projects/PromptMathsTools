var url = "http://127.0.0.1:8921";
const form = document.getElementById("solve-form");
const questionInput = document.getElementById("question-input");
const submitBtn = document.getElementById("submit-btn");

const pipelineSection = document.getElementById("pipeline-section");
const statusPill = document.getElementById("status-pill");
const stepsList = document.getElementById("steps-list");

const answerSection = document.getElementById("answer-section");
const categoryTag = document.getElementById("category-tag");
const answerContent = document.getElementById("answer-content");

// Populate textarea when user clicks a sample Olympiad problem chip
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    questionInput.value = chip.dataset.q;
    questionInput.focus();
  });
});

// Helper to append or update live step rows
function addStep(id, htmlContent, isCompleted = false) {
  let row = document.getElementById(id);
  if (!row) {
    row = document.createElement("div");
    row.id = id;
    row.className = "step-item";
    stepsList.appendChild(row);
  }
  if (isCompleted) row.classList.add("completed");
  row.innerHTML = htmlContent;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  // Reset UI for new run
  submitBtn.disabled = true;
  stepsList.innerHTML = "";
  answerContent.textContent = "";
  answerSection.classList.add("hidden");
  pipelineSection.classList.remove("hidden");

  statusPill.textContent = "Agent Working...";
  statusPill.className = "status-pill running";

  try {
    // Call FastAPI SSE streaming endpoint
    const response = await fetch(url + "/operations/solveProblem", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop(); // Keep any incomplete trailing chunk

      for (const rawEvent of events) {
        if (!rawEvent.startsWith("data: ")) continue;
        const data = JSON.parse(rawEvent.slice(6));

        // 1. Structured Classifier Events
        if (data.stage === "classifier") {
          if (data.status === "running") {
            addStep(
              "step-classifier",
              `<span class="spinner"></span><div><strong>[Router]</strong> ${data.message}</div>`
            );
          } else if (data.status === "done") {
            categoryTag.textContent = data.category.toUpperCase();
            const timeTag = data.duration_ms ? `<span class="meta-time">(${data.duration_ms} ms)</span>` : "";
            addStep(
              "step-classifier",
              `<span>🧭</span>
               <div class="verbose-block">
                 <div><strong>[Structured Classifier]</strong> Category: <span class="step-code">${data.category}</span> ${timeTag}</div>
                 <div class="verbose-sub">Planned Tools: <span class="step-code">${data.planned_tools.join(", ") || "auto"}</span></div>
               </div>`,
              true
            );
          }
        }

        // 2. LLM Reasoning / Planning Turn
        if (data.stage === "llm") {
          addStep(
            "step-llm-think",
            `<span class="spinner"></span><div><strong>[Agent Brain]</strong> ${data.message}</div>`
          );
        }

        // 3. Verbose Python Tool Execution Events (matched cleanly by run_id)
        if (data.stage === "tool") {
          const llmRow = document.getElementById("step-llm-think");
          if (llmRow) llmRow.remove();

          const stepId = `tool-${data.run_id || data.tool}`;
          const argsFormatted = JSON.stringify(data.args);

          if (data.status === "running") {
            addStep(
              stepId,
              `<span class="spinner"></span>
               <div class="verbose-block">
                 <div><strong>[Tool Invoked]</strong> <span class="step-code">${data.tool}</span></div>
                 <div class="verbose-sub">Input Args: <span class="step-code">${argsFormatted}</span></div>
               </div>`
            );
          } else if (data.status === "done") {
            const timeTag = data.duration_ms ? `<span class="meta-time">(${data.duration_ms} ms)</span>` : "";
            addStep(
              stepId,
              `<span>⚙️</span>
               <div class="verbose-block">
                 <div><strong>[Tool Completed]</strong> <span class="step-code">${data.tool}</span> ${timeTag}</div>
                 <div class="verbose-sub">Input Args: <span class="step-code">${argsFormatted}</span></div>
                 <div class="verbose-sub">Return Output: <span class="step-code">${data.output}</span></div>
               </div>`,
              true
            );
          }
        }

        // 4. Final Official Solution (Displayed prominently at top)
        if (data.stage === "complete") {
          const llmRow = document.getElementById("step-llm-think");
          if (llmRow) llmRow.remove();

          statusPill.textContent = "Solved ✓";
          statusPill.className = "status-pill done";
          answerContent.textContent = data.answer;
          answerSection.classList.remove("hidden");
        }

        // 5. Error Handling
        if (data.stage === "error") {
          const llmRow = document.getElementById("step-llm-think");
          if (llmRow) llmRow.remove();

          statusPill.textContent = "Error";
          addStep("step-error", `<span>❌</span><div><strong>Error:</strong> ${data.message}</div>`);
        }
      }
    }
  } catch (err) {
    statusPill.textContent = "Connection Failed";
    addStep("step-net-err", `<span>❌</span><div><strong>Request Error:</strong> ${err.message}</div>`);
  } finally {
    submitBtn.disabled = false;
  }
});
