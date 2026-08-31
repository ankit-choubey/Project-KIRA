/**
 * React Hook for Loading and Caching Immutable Artifacts
 */

import { useState, useEffect } from "react";
import { source } from "./source";

const artifactCache = new Map<string, any>();
const pendingPromises = new Map<string, Promise<any>>();

export interface UseArtifactResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  missing: boolean;
  reload: () => Promise<void>;
}

export function useArtifact<T = any>(artifactName?: string | null): UseArtifactResult<T> {
  const [data, setData] = useState<T | null>(() => {
    if (!artifactName) return null;
    return artifactCache.get(artifactName) ?? null;
  });
  const [loading, setLoading] = useState<boolean>(() => {
    if (!artifactName) return false;
    return !artifactCache.has(artifactName);
  });
  const [error, setError] = useState<Error | null>(null);
  const [missing, setMissing] = useState<boolean>(false);

  const fetchArtifact = async () => {
    if (!artifactName) {
      setData(null);
      setLoading(false);
      setMissing(false);
      return;
    }

    if (artifactCache.has(artifactName)) {
      setData(artifactCache.get(artifactName));
      setLoading(false);
      setMissing(false);
      return;
    }

    setLoading(true);
    setError(null);
    setMissing(false);

    try {
      let promise = pendingPromises.get(artifactName);
      if (!promise) {
        promise = source.loadArtifact<T>(artifactName);
        pendingPromises.set(artifactName, promise);
      }

      const result = await promise;
      artifactCache.set(artifactName, result);
      pendingPromises.delete(artifactName);

      setData(result);
      setMissing(false);
    } catch (err: any) {
      pendingPromises.delete(artifactName);
      if (err?.status === 404) {
        setMissing(true);
      } else {
        setError(err instanceof Error ? err : new Error(String(err)));
      }
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArtifact();
  }, [artifactName]);

  return {
    data,
    loading,
    error,
    missing,
    reload: fetchArtifact,
  };
}
