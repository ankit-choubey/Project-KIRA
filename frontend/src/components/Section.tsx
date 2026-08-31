import React, { Component, type ReactNode } from "react";
import { useArtifact } from "../data/useArtifact";

interface ErrorBoundaryProps {
  sectionTitle: string;
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class SectionErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="card awaiting-data-banner">
          <strong>Section Error ({this.props.sectionTitle})</strong>
          <p className="unmeasured" style={{ margin: 0 }}>
            {this.state.error?.message || "An unexpected error occurred while rendering this section."}
          </p>
        </div>
      );
    }
    return this.props.children;
  }
}

interface SectionProps {
  id: string;
  tagline?: string;
  title: string;
  description?: string;
  requiredArtifact?: string;
  badge?: ReactNode;
  children: ReactNode;
}

export const Section: React.FC<SectionProps> = ({
  id,
  tagline,
  title,
  description,
  requiredArtifact,
  badge,
  children,
}) => {
  // If a specific required artifact is declared, check its presence
  const artifactCheck = useArtifact(requiredArtifact || "manifest.json");

  const shouldRenderAwaiting = requiredArtifact && artifactCheck.missing;

  return (
    <section id={id} className="section-wrapper" aria-labelledby={`heading-${id}`}>
      <header className="section-header">
        {tagline && <span className="section-tagline">{tagline}</span>}
        <div className="section-title-row">
          <h2 id={`heading-${id}`}>{title}</h2>
          {badge}
        </div>
        {description && <p className="section-desc">{description}</p>}
      </header>

      <SectionErrorBoundary sectionTitle={title}>
        {shouldRenderAwaiting ? (
          <div className="awaiting-data-banner">
            <strong>AWAITING RUN DATA</strong>
            <p>
              This section depends on <code>{requiredArtifact}</code> which was not found in the resolved run artifacts.
            </p>
          </div>
        ) : (
          children
        )}
      </SectionErrorBoundary>
    </section>
  );
};
