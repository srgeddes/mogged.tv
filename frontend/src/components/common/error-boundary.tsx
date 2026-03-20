import { Component } from "react"
import type { ErrorInfo, ReactNode } from "react"

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Uncaught error:", error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4 text-center">
          <h1 className="font-display text-6xl font-bold tracking-tight text-primary">
            gg, we crashed
          </h1>
          <p className="mt-4 text-lg text-muted-foreground">
            something broke and honestly that's on us. try refreshing.
          </p>
          {this.state.error && (
            <pre className="mt-6 max-w-lg overflow-auto rounded-lg border border-border bg-card p-4 text-left font-mono text-sm text-muted-foreground">
              {this.state.error.message}
            </pre>
          )}
          <button
            onClick={() => window.location.reload()}
            className="mt-8 rounded-lg bg-primary px-6 py-3 font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            try again
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
