import { useMemo, useState } from "react";
import type { ChangeEvent } from "react";
import "./App.css";

type SemanticType = "heading" | "paragraph" | "table" | "list" | "unknown";

interface SemanticBlock {
  page_number: number;
  source_block_index: number;
  semantic_type: SemanticType;
  text: string;
  confidence: number;
  signals: Record<string, unknown>;
}

interface Section {
  heading: string;
  level: number;
  page_start: number | null;
  page_end: number | null;
  blocks: SemanticBlock[];
  children: Section[];
}

interface ExtractionResponse {
  metadata: {
    request_id: string;
    filename: string;
    page_count: number;
    processing_time_ms: number;
    block_count: number;
  };
  sections: Section[];
}

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000/api/extract";

const typeLabels: Record<SemanticType, string> = {
  heading: "Heading",
  paragraph: "Paragraph",
  table: "Table",
  list: "List",
  unknown: "Unknown",
};

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ExtractionResponse | null>(null);
  const [selectedSection, setSelectedSection] = useState(0);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<"all" | SemanticType>("all");
  const [isExtracting, setIsExtracting] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);

  const handleFile = (selectedFile: File | null) => {
    setError("");

    if (!selectedFile) {
      return;
    }

    if (selectedFile.type !== "application/pdf" && !selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setError("Please select a PDF file.");
      return;
    }

    setFile(selectedFile);
    setResult(null);
    setSelectedSection(0);
    setSearch("");
    setTypeFilter("all");
  };

  const handleFileInput = (event: ChangeEvent<HTMLInputElement>) => {
    handleFile(event.target.files?.[0] ?? null);
  };

  const extractDocument = async () => {
    if (!file) {
      setError("Please select a PDF before extracting.");
      return;
    }

    setIsExtracting(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        const message =
          typeof data?.detail === "string"
            ? data.detail
            : "The PDF could not be extracted.";

        throw new Error(message);
      }

      setResult(data);
      setSelectedSection(0);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to connect to the extraction service.",
      );
    } finally {
      setIsExtracting(false);
    }
  };

  const selected = result?.sections[selectedSection];

  const filteredBlocks = useMemo(() => {
    if (!selected) {
      return [];
    }

    const query = search.trim().toLowerCase();

    return selected.blocks.filter((block) => {
      const matchesSearch =
        !query ||
        block.text.toLowerCase().includes(query) ||
        typeLabels[block.semantic_type].toLowerCase().includes(query);

      const matchesType =
        typeFilter === "all" || block.semantic_type === typeFilter;

      return matchesSearch && matchesType;
    });
  }, [selected, search, typeFilter]);

  const totalBlocks = result?.metadata.block_count ?? 0;

  const typeCounts = useMemo(() => {
    if (!selected) {
      return {
        heading: 0,
        paragraph: 0,
        table: 0,
        list: 0,
        unknown: 0,
      };
    }

    return selected.blocks.reduce(
      (counts, block) => {
        counts[block.semantic_type] += 1;
        return counts;
      },
      {
        heading: 0,
        paragraph: 0,
        table: 0,
        list: 0,
        unknown: 0,
      } as Record<SemanticType, number>,
    );
  }, [selected]);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">CE</div>
          <div>
            <div className="brand-name">Comply Extractor</div>
            <div className="brand-subtitle">PDF document intelligence</div>
          </div>
        </div>

        <div className="topbar-status">
          <span className="status-dot" />
          Extraction service
          <span className="status-online">Ready</span>
        </div>
      </header>

      <main className="workspace">
        <section className="page-intro">
          <div>
            <span className="eyebrow">DOCUMENT EXTRACTION</span>
            <h1>Extract and review your PDF</h1>
            <p>
              Upload a PDF to extract structured sections, paragraphs, tables,
              lists, headings, and confidence information.
            </p>
          </div>

          {result && (
            <button
              className="secondary-button"
              onClick={() => {
                setResult(null);
                setFile(null);
                setSearch("");
                setTypeFilter("all");
              }}
            >
              New document
            </button>
          )}
        </section>

        {!result ? (
          <section className="upload-card">
            <div
              className={`drop-zone ${dragActive ? "drag-active" : ""} ${
                file ? "has-file" : ""
              }`}
              onDragOver={(event) => {
                event.preventDefault();
                setDragActive(true);
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(event) => {
                event.preventDefault();
                setDragActive(false);
                handleFile(event.dataTransfer.files?.[0] ?? null);
              }}
            >
              <input
                id="pdf-upload"
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileInput}
              />

              <label htmlFor="pdf-upload" className="drop-content">
                <div className="upload-icon">↑</div>

                {file ? (
                  <>
                    <h2>{file.name}</h2>
                    <p>
                      {(file.size / 1024 / 1024).toFixed(2)} MB · PDF selected
                    </p>
                    <span className="change-file">Choose another file</span>
                  </>
                ) : (
                  <>
                    <h2>Drop your PDF here</h2>
                    <p>or click to browse from your computer</p>
                    <span className="file-hint">PDF files up to 25 MB</span>
                  </>
                )}
              </label>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="upload-actions">
              <div className="selected-file">
                {file ? (
                  <>
                    <span className="pdf-badge">PDF</span>
                    <div>
                      <strong>{file.name}</strong>
                      <small>Ready for extraction</small>
                    </div>
                  </>
                ) : (
                  <span className="muted">No document selected</span>
                )}
              </div>

              <button
                className="primary-button"
                disabled={!file || isExtracting}
                onClick={extractDocument}
              >
                {isExtracting ? (
                  <>
                    <span className="spinner" />
                    Extracting…
                  </>
                ) : (
                  <>Extract document</>
                )}
              </button>
            </div>

            <div className="workflow">
              <div className="workflow-step active">
                <span>1</span>
                <div>
                  <strong>Upload</strong>
                  <small>Select a PDF</small>
                </div>
              </div>

              <div className="workflow-line" />

              <div className="workflow-step">
                <span>2</span>
                <div>
                  <strong>Extract</strong>
                  <small>Analyze document</small>
                </div>
              </div>

              <div className="workflow-line" />

              <div className="workflow-step">
                <span>3</span>
                <div>
                  <strong>Review</strong>
                  <small>Inspect results</small>
                </div>
              </div>
            </div>
          </section>
        ) : (
          <section className="results-layout">
            <aside className="sidebar">
              <div className="sidebar-header">
                <div>
                  <span className="eyebrow">DOCUMENT</span>
                  <h2>Sections</h2>
                </div>
                <span className="section-count">{result.sections.length}</span>
              </div>

              <div className="document-mini">
                <div className="pdf-badge large">PDF</div>
                <div className="document-mini-text">
                  <strong title={result.metadata.filename}>
                    {result.metadata.filename}
                  </strong>
                  <span>
                    {result.metadata.page_count} pages · {totalBlocks} blocks
                  </span>
                </div>
              </div>

              <nav className="section-list">
                {result.sections.map((section, index) => (
                  <button
                    key={`${section.heading}-${index}`}
                    className={`section-item ${
                      selectedSection === index ? "selected" : ""
                    }`}
                    onClick={() => {
                      setSelectedSection(index);
                      setSearch("");
                      setTypeFilter("all");
                    }}
                  >
                    <span className="section-number">
                      {String(index + 1).padStart(2, "0")}
                    </span>

                    <span className="section-item-main">
                      <strong>
                        {section.heading || "Untitled section"}
                      </strong>
                      <small>
                        Pages {section.page_start ?? "—"}–
                        {section.page_end ?? "—"}
                      </small>
                    </span>

                    <span className="section-block-count">
                      {section.blocks.length}
                    </span>
                  </button>
                ))}
              </nav>
            </aside>

            <section className="content-panel">
              <div className="results-header">
                <div>
                  <span className="eyebrow">
                    SECTION {String(selectedSection + 1).padStart(2, "0")}
                  </span>
                  <h2>{selected?.heading || "Untitled section"}</h2>

                  <div className="section-meta">
                    <span>
                      Pages {selected?.page_start ?? "—"}–
                      {selected?.page_end ?? "—"}
                    </span>
                    <span>{selected?.blocks.length ?? 0} blocks</span>
                  </div>
                </div>

                <div className="extraction-summary">
                  <span className="success-icon">✓</span>
                  <div>
                    <strong>Extraction complete</strong>
                    <small>
                      {result.metadata.processing_time_ms.toFixed(0)} ms
                    </small>
                  </div>
                </div>
              </div>

              <div className="stats-row">
                <button
                  className={`stat-card ${
                    typeFilter === "all" ? "active" : ""
                  }`}
                  onClick={() => setTypeFilter("all")}
                >
                  <span className="stat-value">{selected?.blocks.length ?? 0}</span>
                  <span className="stat-label">All blocks</span>
                </button>

                <button
                  className={`stat-card ${
                    typeFilter === "heading" ? "active" : ""
                  }`}
                  onClick={() => setTypeFilter("heading")}
                >
                  <span className="stat-value">{typeCounts.heading}</span>
                  <span className="stat-label">Headings</span>
                </button>

                <button
                  className={`stat-card ${
                    typeFilter === "paragraph" ? "active" : ""
                  }`}
                  onClick={() => setTypeFilter("paragraph")}
                >
                  <span className="stat-value">{typeCounts.paragraph}</span>
                  <span className="stat-label">Paragraphs</span>
                </button>

                <button
                  className={`stat-card ${
                    typeFilter === "table" ? "active" : ""
                  }`}
                  onClick={() => setTypeFilter("table")}
                >
                  <span className="stat-value">{typeCounts.table}</span>
                  <span className="stat-label">Tables</span>
                </button>

                <button
                  className={`stat-card ${
                    typeFilter === "list" ? "active" : ""
                  }`}
                  onClick={() => setTypeFilter("list")}
                >
                  <span className="stat-value">{typeCounts.list}</span>
                  <span className="stat-label">Lists</span>
                </button>
              </div>

              <div className="content-toolbar">
                <div className="search-box">
                  <span className="search-icon">⌕</span>
                  <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search extracted content…"
                  />
                  {search && (
                    <button
                      className="clear-search"
                      onClick={() => setSearch("")}
                    >
                      ×
                    </button>
                  )}
                </div>

                <select
                  value={typeFilter}
                  onChange={(event) =>
                    setTypeFilter(event.target.value as "all" | SemanticType)
                  }
                  className="type-select"
                >
                  <option value="all">All types</option>
                  <option value="heading">Headings</option>
                  <option value="paragraph">Paragraphs</option>
                  <option value="table">Tables</option>
                  <option value="list">Lists</option>
                </select>
              </div>

              <div className="content-results">
                <div className="result-count">
                  Showing {filteredBlocks.length} of {selected?.blocks.length ?? 0}{" "}
                  blocks
                </div>

                {filteredBlocks.length === 0 ? (
                  <div className="empty-results">
                    <div className="empty-icon">⌕</div>
                    <h3>No matching content</h3>
                    <p>Try a different search term or semantic type.</p>
                  </div>
                ) : (
                  <div className="block-list">
                    {filteredBlocks.map((block, index) => (
                      <article
                        className={`content-block type-${block.semantic_type}`}
                        key={`${block.source_block_index}-${index}`}
                      >
                        <div className="block-top">
                          <div className="block-identifiers">
                            <span className={`type-pill ${block.semantic_type}`}>
                              {typeLabels[block.semantic_type]}
                            </span>

                            <span className="page-pill">
                              Page {block.page_number}
                            </span>

                            <span className="source-index">
                              Block #{block.source_block_index}
                            </span>
                          </div>

                          <span className="confidence">
                            {Math.round(block.confidence * 100)}% confidence
                          </span>
                        </div>

                        <div className="block-text">
                          {block.text}
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </div>
            </section>
          </section>
        )}

        {!result && !error && (
          <div className="feature-row">
            <div>
              <span className="feature-icon">▦</span>
              <div>
                <strong>Structured extraction</strong>
                <p>Sections and semantic blocks preserved.</p>
              </div>
            </div>

            <div>
              <span className="feature-icon">⌁</span>
              <div>
                <strong>Layout aware</strong>
                <p>Tables and lists are identified separately.</p>
              </div>
            </div>

            <div>
              <span className="feature-icon">✓</span>
              <div>
                <strong>Confidence signals</strong>
                <p>Review extraction confidence at block level.</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;