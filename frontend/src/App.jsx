import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useEffect, useState } from "react";

import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  MarkerType,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "./App.css";

const API = "http://localhost:5000";

// ============================================================
// API HELPER
// ============================================================


async function apiRequest(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }

  return data;
}


// ============================================================
// BRAND
// ============================================================

function Brand({ light = false }) {
  return (
    <Link to="/" className={`brand ${light ? "brand-light" : ""}`}>
      <span className="brand-mark">M</span>

      <span className="brand-copy">
        <span className="brand-name">MEMORA</span>
        <span className="brand-subtitle">
          Organizational Memory
        </span>
      </span>
    </Link>
  );
}

// ============================================================
// LANDING PAGE
// ============================================================

function Landing() {
  return (
    <div className="landing">
      <header className="landing-header">
        <Brand />

        <nav className="landing-nav">
          <a href="#features">Platform</a>
          <a href="#how-it-works">How it works</a>

          <Link className="nav-login" to="/login">
            Log in
          </Link>

          <Link
            className="button button-primary button-small"
            to="/signup"
          >
            Register company
          </Link>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">
              ENTERPRISE KNOWLEDGE INTELLIGENCE
            </p>

            <h1>
              Your company's knowledge,{" "}
              <span>connected.</span>
            </h1>

            <p className="hero-description">
              MEMORA helps organizations retrieve knowledge from
              enterprise documents and understand the evidence
              behind each answer.
            </p>

            <div className="hero-actions">
              <Link
                to="/signup"
                className="button button-primary"
              >
                Get started <span>→</span>
              </Link>

              <Link
                to="/login"
                className="button button-secondary"
              >
                Company login
              </Link>
            </div>

            <p className="hero-footnote">
              Built for organizational knowledge and evidence-led
              decisions.
            </p>
          </div>

          <div className="hero-preview">
            <div className="preview-top">
              <Brand />
              <span className="preview-label">
                KNOWLEDGE ASSISTANT
              </span>
            </div>

            <div className="preview-content">
              <p className="eyebrow">ASK YOUR ORGANIZATION</p>

              <h2>Find answers in your documents.</h2>

              <p>
                Search indexed knowledge and review the supporting
                evidence retrieved by MEMORA.
              </p>

              <div className="preview-question">
                How should an enterprise upgrade be prepared?
                <span>→</span>
              </div>

              <div className="preview-answer">
                <span className="answer-rule" />

                <div>
                  <strong>Evidence-led answers</strong>
                  <p>
                    Review retrieved sources and verification status.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="feature-section" id="features">
          <div className="section-intro">
            <p className="eyebrow">THE MEMORA PLATFORM</p>

            <h2>
              Knowledge that works for your organization.
            </h2>

            <p>
              Bring enterprise knowledge together in one workspace.
            </p>
          </div>

          <div className="feature-grid">
            <article className="feature-card">
              <span className="feature-index">01</span>
              <h3>Knowledge retrieval</h3>
              <p>
                Search indexed documents using semantic retrieval
                and reranking.
              </p>
            </article>

            <article className="feature-card">
              <span className="feature-index">02</span>
              <h3>Evidence-backed answers</h3>
              <p>
                Review the sources returned alongside answers and
                their verification status.
              </p>
            </article>

            <article className="feature-card">
              <span className="feature-index">03</span>
              <h3>Connected knowledge</h3>
              <p>
                Build toward a connected organizational knowledge
                graph and shared workspace.
              </p>
            </article>
          </div>
        </section>

        <section className="how-section" id="how-it-works">
          <div>
            <p className="eyebrow">GET STARTED</p>
            <h2>A workspace for your company.</h2>
            <p>
              Register your organization, log in, and use the
              knowledge assistant.
            </p>
          </div>

          <Link
            to="/signup"
            className="button button-primary"
          >
            Create company account →
          </Link>
        </section>
      </main>

      <footer className="public-footer">
        <Brand />
        <span>
          Organizational memory, grounded in evidence.
        </span>
      </footer>
    </div>
  );
}

// ============================================================
// AUTHENTICATION LAYOUT
// ============================================================

function AuthLayout({
  title,
  description,
  children,
  footer,
}) {
  return (
    <main className="auth-page">
      <aside className="auth-aside">
        <Brand light />

        <div className="auth-aside-copy">
          <p className="eyebrow">
            MEMORA FOR ORGANIZATIONS
          </p>

          <h1>
            Make organizational knowledge accessible.
          </h1>

          <p>
            A dedicated workspace for enterprise knowledge
            retrieval, evidence, and connected organizational memory.
          </p>
        </div>

        <span className="auth-aside-footer">
          MEMORA · Enterprise knowledge
        </span>
      </aside>

      <section className="auth-main">
        <div className="auth-form-wrap">
          <Link className="back-link" to="/">
            ← Back to home
          </Link>

          <p className="eyebrow">COMPANY WORKSPACE</p>

          <h2>{title}</h2>

          <p className="auth-description">
            {description}
          </p>

          {children}

          <div className="auth-switch">
            {footer}
          </div>
        </div>
      </section>
    </main>
  );
}

// ============================================================
// SIGNUP PAGE
// ============================================================

function SignUp() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    company_name: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function update(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function submit(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      await apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify(form),
      });

      // Registration succeeds, but does not automatically log in.
      navigate("/login", {
        replace: true,
        state: {
          registered: true,
          email: form.email.trim().toLowerCase(),
        },
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Register your company"
      description="Create a company workspace and its administrator account."
      footer={
        <>
          Already registered? <Link to="/login">Log in</Link>
        </>
      }
    >
      <form className="auth-form" onSubmit={submit}>
        <label>
          Your full name
          <input
            name="name"
            value={form.name}
            onChange={update}
            placeholder="Enter your name"
            autoComplete="name"
            required
          />
        </label>

        <label>
          Company name
          <input
            name="company_name"
            value={form.company_name}
            onChange={update}
            placeholder="Enter your organization"
            autoComplete="organization"
            required
          />
        </label>

        <label>
          Work email
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={update}
            placeholder="you@company.com"
            autoComplete="email"
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={update}
            placeholder="At least 8 characters"
            autoComplete="new-password"
            minLength={8}
            maxLength={72}
            required
          />
        </label>

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}

        <button
          type="submit"
          className="button button-primary auth-submit"
          disabled={loading}
        >
          {loading
            ? "Creating workspace..."
            : "Create company account"}
        </button>

        <p className="form-note">
          Registration creates a company workspace and administrator
          account for this development instance.
        </p>
      </form>
    </AuthLayout>
  );
}

// ============================================================
// LOGIN PAGE
// ============================================================

function Login({ onAuthenticated }) {
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState(
    location.state?.email || ""
  );

  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const [notice] = useState(
    location.state?.registered
      ? "Company registered successfully. Please log in to continue."
      : ""
  );

  const [loading, setLoading] = useState(false);

  async function submit(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const data = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password,
        }),
      });

      // Update React authentication state immediately.
      onAuthenticated(data.user);

      // Navigate only after the login API returns success.
      navigate("/app", {
        replace: true,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Welcome back"
      description="Log in to your organization's MEMORA workspace."
      footer={
        <>
          New to MEMORA?{" "}
          <Link to="/signup">Register your company</Link>
        </>
      }
    >
      <form className="auth-form" onSubmit={submit}>
        {notice && (
          <p className="form-success" role="status">
            {notice}
          </p>
        )}

        <label>
          Work email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@company.com"
            autoComplete="username"
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter your password"
            autoComplete="current-password"
            required
          />
        </label>

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}

        <button
          type="submit"
          className="button button-primary auth-submit"
          disabled={loading}
        >
          {loading ? "Signing in..." : "Log in to MEMORA"}
        </button>
      </form>
    </AuthLayout>
  );
}

// ============================================================
// PROTECTED ROUTE
// ============================================================

function ProtectedRoute({
  user,
  checking,
  children,
}) {
  const location = useLocation();

  if (checking) {
    return (
      <div className="page-loading">
        Loading your workspace...
      </div>
    );
  }

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location.pathname }}
      />
    );
  }

  return children;
}


const SAMPLE_NODES = [
  {
    id: "1",
    type: "default",
    position: { x: 60, y: 140 },
    data: {
      label: "Upgrade Guide",
      category: "Document",
      description: "Sample document describing an enterprise upgrade process.",
    },
  },
  {
    id: "2",
    position: { x: 340, y: 50 },
    data: {
      label: "Backup Strategy",
      category: "Decision",
      description: "Sample decision about backup and recovery preparation.",
    },
  },
  {
    id: "3",
    position: { x: 340, y: 230 },
    data: {
      label: "Engineering Team",
      category: "Team",
      description: "Sample team associated with upgrade preparation.",
    },
  },
  {
    id: "4",
    position: { x: 630, y: 140 },
    data: {
      label: "Rollback Plan",
      category: "Document",
      description: "Sample document describing a rollback plan.",
    },
  },
  {
    id: "5",
    position: { x: 630, y: 330 },
    data: {
      label: "Deployment Risk",
      category: "Risk",
      description: "Sample risk associated with deployment readiness.",
    },
  },
];

const SAMPLE_EDGES = [
  {
    id: "e1-2",
    source: "1",
    target: "2",
    label: "describes",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "e1-3",
    source: "1",
    target: "3",
    label: "involves",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "e2-4",
    source: "2",
    target: "4",
    label: "supports",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "e3-5",
    source: "3",
    target: "5",
    label: "monitors",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "e4-5",
    source: "4",
    target: "5",
    label: "mitigates",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
];

function KnowledgeGraph() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [selectedNode, setSelectedNode] = useState(null);

  const categories = [
    "All",
    "Document",
    "Decision",
    "Team",
    "Risk",
  ];

  const filteredNodes = SAMPLE_NODES.filter((node) => {
    const matchesCategory =
      category === "All" || node.data.category === category;

    const matchesSearch = (
      node.data.label + " " +
      node.data.category + " " +
      node.data.description
    ).toLowerCase().includes(search.toLowerCase());

    return matchesCategory && matchesSearch;
  });

  const visibleIds = new Set(filteredNodes.map((node) => node.id));

  const filteredEdges = SAMPLE_EDGES.filter(
    (edge) =>
      visibleIds.has(edge.source) &&
      visibleIds.has(edge.target)
  );

  const selected = filteredNodes.find(
    (node) => node.id === selectedNode?.id
  );

  return (
    <section className="graph-page">
      <div className="page-heading">
        <p className="eyebrow">CONNECTED ORGANIZATIONAL KNOWLEDGE</p>
        <h1>Knowledge Graph</h1>
        <p className="page-description">
          Explore how documents, teams, decisions, and risks connect.
        </p>
      </div>

      <div className="graph-notice">
        <strong>Preview mode</strong>
        <span>
          These are illustrative sample records, not actual company data.
          Neo4j integration is pending.
        </span>
      </div>

      <div className="graph-toolbar">
        <input
          aria-label="Search graph entities"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search entities..."
        />

        <select
          aria-label="Filter entities by type"
          value={category}
          onChange={(event) => setCategory(event.target.value)}
        >
          {categories.map((item) => (
            <option key={item} value={item}>
              {item === "All" ? "All entity types" : item}
            </option>
          ))}
        </select>

        <button
          type="button"
          className="graph-reset"
          onClick={() => {
            setSearch("");
            setCategory("All");
            setSelectedNode(null);
          }}
        >
          Reset
        </button>
      </div>

      <div className="graph-stats">
        <div>
          <strong>{filteredNodes.length}</strong>
          <span>Visible entities</span>
        </div>
        <div>
          <strong>{filteredEdges.length}</strong>
          <span>Relationships</span>
        </div>
        <div>
          <strong>{categories.length - 1}</strong>
          <span>Entity types</span>
        </div>
      </div>

      <div className="graph-workspace">
        <div className="graph-canvas">
          {filteredNodes.length > 0 ? (
            <ReactFlow
              key={`${category}-${search}`}
              nodes={filteredNodes.map((node) => ({
                ...node,
                selected: node.id === selectedNode?.id,
                style: {
                  background: "#ffffff",
                  color: "#292326",
                  border: node.id === selectedNode?.id
                    ? "2px solid #6d1f35"
                    : "1px solid #e9e4e6",
                  borderRadius: 9,
                  padding: 12,
                  width: 175,
                  fontSize: 12,
                  boxShadow: "0 4px 14px #32101b10",
                },
              }))}
              edges={filteredEdges.map((edge) => ({
                ...edge,
                style: { stroke: "#9c7180", strokeWidth: 1.5 },
                labelStyle: { fill: "#6d1f35", fontSize: 10 },
                labelBgStyle: { fill: "#ffffff" },
              }))}
              fitView
              fitViewOptions={{ padding: 0.25 }}
              nodesDraggable
              nodesConnectable={false}
              elementsSelectable
              onNodeClick={(_, node) => setSelectedNode(node)}
              proOptions={{ hideAttribution: true }}
            >
              <Background color="#e9e4e6" gap={22} />
              <Controls />
              <MiniMap
                nodeColor="#6d1f35"
                maskColor="rgba(246,244,242,0.65)"
              />
            </ReactFlow>
          ) : (
            <div className="graph-empty">
              <h3>No matching entities</h3>
              <p>Try another search term or entity type.</p>
            </div>
          )}
        </div>

        <aside className="graph-details">
          <span className="placeholder-label">ENTITY DETAILS</span>

          {selected ? (
            <>
              <h2>{selected.data.label}</h2>
              <span className="graph-type">
                {selected.data.category}
              </span>
              <p>{selected.data.description}</p>

              <h3>Connected entities</h3>
              {SAMPLE_EDGES
                .filter(
                  (edge) =>
                    edge.source === selected.id ||
                    edge.target === selected.id
                )
                .map((edge) => {
                  const otherId =
                    edge.source === selected.id
                      ? edge.target
                      : edge.source;

                  const other = SAMPLE_NODES.find(
                    (node) => node.id === otherId
                  );

                  return (
                    <div className="graph-connection" key={edge.id}>
                      <strong>{other?.data.label}</strong>
                      <span>{edge.label}</span>
                    </div>
                  );
                })}
            </>
          ) : (
            <>
              <h2>Select an entity</h2>
              <p>
                Click any node in the graph to inspect its details
                and connected entities.
              </p>
            </>
          )}
        </aside>
      </div>

      <p className="graph-footnote">
        Sample relationships are illustrative and have not been
        verified against company documents.
      </p>
    </section>
  );
}


// ============================================================
// EXPERTS
// ============================================================


function Experts() {
  const [experts, setExperts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] = useState("All");

  useEffect(() => {
    let active = true;

    apiRequest("/experts")
      .then((data) => {
        if (active) {
          setExperts(Array.isArray(data.experts) ? data.experts : []);
        }
      })
      .catch((err) => {
        if (active) setError(err.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const filteredExperts = experts.filter((expert) => {
    const query = searchTerm.trim().toLowerCase();

    const evidenceRecords = Array.isArray(expert.evidence)
      ? expert.evidence
      : expert.evidence
        ? [expert.evidence]
        : [];

    const name =
      expert.name ||
      expert.person_name ||
      expert.person ||
      "";

    const searchableText = [
      name,
      expert.role,
      ...(expert.roles || []),
      ...evidenceRecords.flatMap((item) => [
        item.document_title,
        item.role,
        item.source_type,
        item.context,
      ]),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    const matchesSearch = searchableText.includes(query);

    const roles = [
      expert.role,
      ...(expert.roles || []),
      ...evidenceRecords.map((item) => item.role),
    ].filter(Boolean);

    const matchesRole =
      roleFilter === "All" || roles.includes(roleFilter);

    return matchesSearch && matchesRole;
  });

  return (
    <section className="experts-page">
      <div className="page-heading">
        <p className="eyebrow">COMPANY KNOWLEDGE</p>
        <h1>Experts</h1>
        <p className="page-description">
          People and role references identified in indexed enterprise documents.
        </p>
      </div>

      <div className="graph-notice">
        <strong>Evidence-based extraction</strong>
        <span>
          These are candidate people references found in documents.
          A contact or document owner is not automatically confirmed
          as an employee or subject-matter expert.
        </span>
      </div>

      {loading && (
        <div className="feedback-panel">
          <h3>Finding people references</h3>
          <p>Loading records extracted from enterprise documents.</p>
          <div className="loading-bar" />
        </div>
      )}

      {error && (
        <div className="feedback-panel error-panel">
          <h3>Unable to load Experts</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="experts-toolbar">
            <input
              type="text"
              placeholder="Search people or documents..."
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
            />

            <select
              value={roleFilter}
              onChange={(event) => setRoleFilter(event.target.value)}
            >
              <option value="All">All Roles</option>
              <option value="Document Owner">Document Owner</option>
              <option value="Contact">Contact</option>
              <option value="Reviewer">Reviewer</option>
              <option value="Escalation Owner">Escalation Owner</option>
            </select>

            <button
              type="button"
              onClick={() => {
                setSearchTerm("");
                setRoleFilter("All");
              }}
            >
              Clear
            </button>
          </div>

          <p className="experts-result-count">
            Showing {filteredExperts.length} of {experts.length} people
          </p>

          <div className="graph-stats">
            <div>
              <strong>{experts.length}</strong>
              <span>People references</span>
            </div>
          </div>

          {filteredExperts.length === 0 ? (
            <div className="placeholder-panel">
              <h2>No matching people found</h2>
              <p>
                Try another name, document title or role.
              </p>
            </div>
          ) : (
            <div className="overview-grid">
              {filteredExperts.map((expert, index) => {
                const evidenceRecords = Array.isArray(expert.evidence)
                  ? expert.evidence
                  : expert.evidence
                    ? [expert.evidence]
                    : [];

                const name =
                  expert.name ||
                  expert.person_name ||
                  expert.person ||
                  "Unnamed person";

                const firstEvidence = evidenceRecords[0] || {};

                const role =
                  expert.role ||
                  firstEvidence.role ||
                  (expert.roles || []).join(", ") ||
                  "Role not specified";

                return (
                  <article
                    className="placeholder-panel"
                    key={`${name}-${index}`}
                  >
                    <span className="placeholder-label">
                      {role}
                    </span>

                    <h2>{name}</h2>

                    <p>
                      <strong>Evidence records:</strong>{" "}
                      {evidenceRecords.length}
                    </p>

                    {evidenceRecords.map((item, evidenceIndex) => (
                      <details
                        className="evidence-item"
                        key={evidenceIndex}
                      >
                        <summary>
                          {item.document_title || "Source document"}
                        </summary>

                        <p>
                          <strong>Role:</strong>{" "}
                          {item.role || "Not specified"}
                        </p>

                        <p>
                          <strong>Source:</strong>{" "}
                          {item.source_type || "Not specified"}
                        </p>

                        <p>
                          <strong>Context:</strong>{" "}
                          {typeof item.context === "string"
                            ? item.context
                            : "No context available."}
                        </p>
                      </details>
                    ))}
                  </article>
                );
              })}
            </div>
          )}
        </>
      )}
    </section>
  );
}


// ============================================================
// WORKSPACE
// ============================================================

function Workspace({ user, onLogout }) {
  const [page, setPage] = useState("overview");
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const items = [
    ["overview", "Overview"],
    ["ask", "Ask MEMORA"],
    ["graph", "Knowledge Graph"],
    ["experts", "Experts"],
    ["decisions", "Decisions"],
    ["risks", "Risks"],
    ["settings", "Company settings"],
  ];

  async function askMemora(question = query) {
    if (!question.trim() || loading) {
      return;
    }

    setPage("ask");
    setQuery(question);
    setResult(null);
    setError("");
    setLoading(true);

    try {
      const data = await apiRequest("/ask", {
        method: "POST",
        body: JSON.stringify({
          query: question.trim(),
        }),
      });

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    try {
      await apiRequest("/auth/logout", {
        method: "POST",
      });
    } catch (err) {
      console.error("Logout request failed:", err);
    } finally {
      onLogout();
    }
  }

  return (
    <div className="workspace-shell">
      <aside className="workspace-sidebar">
        <Brand />

        <p className="nav-heading">
          COMPANY WORKSPACE
        </p>

        <nav className="workspace-nav">
          {items.map(([id, label]) => (
            <button
              key={id}
              type="button"
              className={`workspace-nav-item ${
                page === id ? "active" : ""
              }`}
              onClick={() => {
                setPage(id);
                setError("");
              }}
            >
              <span className="nav-indicator" />
              {label}
            </button>
          ))}
        </nav>

        <div className="workspace-account">
          <div className="account-avatar">
            {(user.name || "A").charAt(0).toUpperCase()}
          </div>

          <div className="account-details">
            <strong>{user.name}</strong>
            <span>
              {user.role} · {user.company?.name}
            </span>
          </div>

          <button
            type="button"
            className="logout-button"
            onClick={logout}
          >
            Log out
          </button>
        </div>
      </aside>

      <main className="workspace-main">
        <header className="workspace-topbar">
          <div>
            <span className="breadcrumb">
              {user.company?.name} /
            </span>{" "}
            <strong>
              {items.find(([id]) => id === page)?.[1]}
            </strong>
          </div>

          <span className="workspace-label">
            COMPANY WORKSPACE
          </span>
        </header>

        <div className="workspace-content">
          {/* OVERVIEW */}
          {page === "overview" && (
            <>
              <div className="page-heading">
                <p className="eyebrow">
                  ORGANIZATIONAL INTELLIGENCE
                </p>

                <h1>Welcome, {user.name}</h1>

                <p className="page-description">
                  Your workspace for enterprise knowledge and evidence.
                </p>
              </div>

              <form
                className="overview-search"
                onSubmit={(event) => {
                  event.preventDefault();
                  askMemora();
                }}
              >
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Ask MEMORA a question..."
                />

                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                >
                  Search
                </button>
              </form>

              <div className="overview-grid">
                {[
                  [
                    "01",
                    "Ask MEMORA",
                    "Search indexed enterprise documents.",
                    "ask",
                  ],
                  [
                    "02",
                    "Knowledge Graph",
                    "Explore connected organizational knowledge.",
                    "graph",
                  ],
                  [
                    "03",
                    "Company settings",
                    "Manage your workspace.",
                    "settings",
                  ],
                ].map(([number, title, description, target]) => (
                  <button
                    type="button"
                    className="overview-card"
                    key={target}
                    onClick={() => setPage(target)}
                  >
                    <span className="card-number">
                      {number}
                    </span>

                    <h3>{title}</h3>
                    <p>{description}</p>

                    <span className="card-link">
                      Open section →
                    </span>
                  </button>
                ))}
              </div>
            </>
          )}


          {/* ASK MEMORA */}
          {page === "ask" && (
            <>
              <div className="page-heading">
                <p className="eyebrow">
                  RETRIEVAL-AUGMENTED GENERATION
                </p>

                <h1>Ask MEMORA</h1>

                <p className="page-description">
                  Ask a question and inspect the retrieved evidence.
                </p>
              </div>

              <form
                className="ask-search"
                onSubmit={(event) => {
                  event.preventDefault();
                  askMemora();
                }}
              >
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Ask about your enterprise knowledge..."
                />

                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                >
                  {loading ? "Searching..." : "Ask"}
                </button>
              </form>

              {loading && (
                <div className="feedback-panel">
                  <h3>Searching enterprise knowledge</h3>
                  <p>
                    Retrieving evidence and checking the response.
                  </p>
                  <div className="loading-bar" />
                </div>
              )}

              {error && (
                <div className="feedback-panel error-panel">
                  <h3>Unable to complete your request</h3>
                  <p>{error}</p>
                </div>
              )}

              {!result && !loading && !error && (
                <div className="suggestions">
                  <h2>Suggested questions</h2>

                  {[
                    "What must be completed before an enterprise Private deployment upgrade begins?",
                    "What does the backup and restore strategy cover?",
                    "How should an upgrade rollback be prepared?",
                  ].map((question) => (
                    <button
                      type="button"
                      className="suggestion"
                      key={question}
                      onClick={() => askMemora(question)}
                    >
                      <span>{question}</span>
                      <span>→</span>
                    </button>
                  ))}
                </div>
              )}

              {result && (
                <div className="answer-layout">
                  <article className="answer-card">
                    <div className="section-heading">
                      <h2>Answer</h2>

                      <span
                        className={`status-badge ${
                          result.verified
                            ? "status-verified"
                            : "status-unverified"
                        }`}
                      >
                        {result.verified ? "Verified" : "Unverified"}
                      </span>
                    </div>

                    <p className="submitted-question">
                      {result.query || query}
                    </p>

                    <div className="markdown-answer">

<ReactMarkdown
  remarkPlugins={[remarkGfm]}
  components={{
    h1: ({ children }) => <h2>{children}</h2>,
    p: ({ children }) => {
      const makeEvidenceClickable = (nodes) =>
        React.Children.map(nodes, (node) => {
          if (typeof node !== "string") return node;

          return node.split(/(\[Evidence\s+\d+\])/gi).map(
            (part, index) => {
              const match = part.match(/\[Evidence\s+(\d+)\]/i);

              if (!match) return part;

              const evidenceNumber = Number(match[1]);

              return (
                <a
                  key={`${part}-${index}`}
                  href={`#evidence-${evidenceNumber}`}
                  onClick={(event) => {
                    event.preventDefault();

                    const target = document.getElementById(
                      `evidence-${evidenceNumber}`
                    );

                    if (target) {
                      target.open = true;
                      target.scrollIntoView({
                        behavior: "smooth",
                        block: "center",
                      });
                    }
                  }}
                >
                  {part}
                </a>
              );
            }
          );
        });

      return <p>{makeEvidenceClickable(children)}</p>;
    },
  }}
>
  {(result.answer || "")
    .replace(/^\s*#{1,2}\s*Answer\s*\n*/i, "")
    .replace(/^\s*Answer\s+/i, "")
    .trim()}
</ReactMarkdown>

                    </div>

                    {result.verification_reason && (
                      <p className="verification-note">
                        {result.verification_reason}
                      </p>
                    )}
                  </article>

                  <aside className="evidence-card">
                    <h2>Evidence sources</h2>

                    <p className="evidence-count">
                      {(result.sources ?? []).length} sources retrieved
                    </p>

                    {(result.sources ?? []).map((source, index) => (
                      <details
                        className="evidence-item"
                        key={source.evidence_id || index}
                        id={`evidence-${index + 1}`}
                      >
                        <summary>
                          {source.evidence_id ||
                            `Evidence ${index + 1}`}

                          <strong>
                            {source.title || "Source document"}
                          </strong>
                        </summary>

                        <p>{source.content || "No source content available."}</p>
                      </details>
                    ))}
                  </aside>
                </div>
              )}
            </>
          )}


          {/* OTHER WORKSPACE SECTIONS */}
          {page === "graph" && <KnowledgeGraph />}
          {page === "experts" && <Experts />}
          {page !== "overview" &&
            page !== "ask" &&
            page !== "graph" &&
            page !== "experts" && (
            <section>
              <div className="page-heading">
                <p className="eyebrow">
                  COMPANY KNOWLEDGE
                </p>

                <h1>
                  {items.find(([id]) => id === page)?.[1]}
                </h1>

                <p className="page-description">
                  {page === "settings"
                    ? "Your company profile and workspace information."
                    : "This module will be connected to its backend as the integration becomes available."}
                </p>
              </div>

              {page === "settings" ? (
                <div className="placeholder-panel">
                  <span className="placeholder-label">
                    COMPANY PROFILE
                  </span>

                  <h2>{user.company?.name}</h2>
                  <p>Administrator: {user.name}</p>
                  <p>Account email: {user.email}</p>
                  <p>Role: {user.role}</p>
                </div>
              ) : (
                <div className="placeholder-panel">
                  <span className="placeholder-label">
                    INTEGRATION PENDING
                  </span>

                  <h2>This module is not connected yet.</h2>

                  <p>
                    This section will show real company data when
                    its backend integration is ready. No sample
                    records are shown as real data.
                  </p>
                </div>
              )}
            </section>
          )}
        </div>

        <footer className="app-footer">
          MEMORA · {user.company?.name}
          <span>Evidence-led enterprise knowledge</span>
        </footer>
      </main>
    </div>
  );
}

// ============================================================
// APPLICATION ROUTES AND SESSION CHECKING
// ============================================================

function AppRoutes() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);

  const location = useLocation();

  useEffect(() => {
  let active = true;

  apiRequest("/auth/me")
    .then((data) => {
      if (active) setUser(data.user);
    })
    .catch(() => {
      if (active) setUser(null);
    })
    .finally(() => {
      if (active) setChecking(false);
    });

  return () => {
    active = false;
  };
}, []);

  // Wait for session validation before deciding access to /app.
  if (checking && location.pathname === "/app") {
    return (
      <div className="page-loading">
        Loading your workspace...
      </div>
    );
  }

  return (
    <Routes>
      <Route
        path="/"
        element={<Landing />}
      />

      <Route
        path="/signup"
        element={
          user
            ? <Navigate to="/app" replace />
            : <SignUp />
        }
      />

      <Route
        path="/login"
        element={
          user
            ? <Navigate to="/app" replace />
            : <Login onAuthenticated={setUser} />
        }
      />

      <Route
        path="/app"
        element={
          <ProtectedRoute
            user={user}
            checking={checking}
          >
            <Workspace
              user={user}
              onLogout={() => {
                setUser(null);
                window.location.replace("/login");
              }}
            />
          </ProtectedRoute>
        }
      />

      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />
    </Routes>
  );
}

// ============================================================
// MAIN APP
// ============================================================

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}