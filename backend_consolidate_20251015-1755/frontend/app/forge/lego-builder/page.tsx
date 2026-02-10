'use client';

import { useState } from 'react';

type GeneratedItem = {
  module: string;
  resource_name: string;
  output_dir: string;
  files: Record<string, string>;
};

type GenerateResponse = {
  requirements_text: string;
  generated?: GeneratedItem[];
};

type ModuleInfo = {
  name: string;
  category: string;
  tags: string[];
  description?: string;
};

export default function LegoBuilderPage() {
  const [requirements, setRequirements] = useState(
    'Quiero un ecommerce con catálogo de productos y checkout con órdenes y pagos.'
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<GenerateResponse | null>(null);
  const [modules, setModules] = useState<ModuleInfo[]>([]);
  const [resources, setResources] = useState<Record<string, any> | null>(null);

  async function loadModules() {
    try {
      setError(null);
      // API routes locales de Next -> proxy al backend
      const [modsRes, resRes] = await Promise.all([
        fetch('/api/forge/modules'),
        fetch('/api/forge/module_resources'),
      ]);

      if (!modsRes.ok) throw new Error('Error loading modules');
      if (!resRes.ok) throw new Error('Error loading module resources');

      const modsJson = await modsRes.json();
      const resJson = await resRes.json();

      setModules(modsJson);
      setResources(resJson);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Error loading modules');
    }
  }

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch('/api/forge/generate_from_requirements', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ requirements_text: requirements }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Error ${res.status}`);
      }

      const json = (await res.json()) as GenerateResponse;
      setResponse(json);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to generate');
    } finally {
      setLoading(false);
    }
  }

  function handleDownloadDemo() {
    // Dispara descarga del ZIP demo_ecommerce vía API route de Next
    window.location.href = '/api/forge/projects/demo_ecommerce/download';
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <main className="max-w-5xl mx-auto py-10 px-4 space-y-8">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold">
            Forge Lego Builder (Backend)
          </h1>
          <p className="text-sm text-slate-400">
            Escribe requisitos en lenguaje natural y genera recursos
            backend (models, schemas, services, routers). Luego
            descarga el proyecto empaquetado.
          </p>
        </header>

        {/* Panel principal */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* Columna izquierda: requisitos + acciones */}
          <section className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Requisitos (free text)
              </label>
              <textarea
                className="w-full h-32 rounded-md bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                value={requirements}
                onChange={(e) => setRequirements(e.target.value)}
              />
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                onClick={handleGenerate}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-md bg-emerald-600 hover:bg-emerald-500 px-4 py-2 text-sm font-medium disabled:opacity-50"
              >
                {loading ? 'Generando...' : 'Generar backend desde requisitos'}
              </button>

              <button
                type="button"
                onClick={loadModules}
                className="inline-flex items-center gap-2 rounded-md bg-slate-800 hover:bg-slate-700 px-4 py-2 text-sm"
              >
                Ver módulos Lego disponibles
              </button>

              <button
                type="button"
                onClick={handleDownloadDemo}
                className="inline-flex items-center gap-2 rounded-md bg-indigo-600 hover:bg-indigo-500 px-4 py-2 text-sm font-medium"
              >
                Descargar demo_ecommerce.zip
              </button>
            </div>

            {error && (
              <p className="text-sm text-red-400 mt-2">Error: {error}</p>
            )}

            <p className="text-xs text-slate-500 mt-2">
              Nota: la descarga de <code>demo_ecommerce.zip</code> requiere
              que el backend haya empaquetado previamente el proyecto
              (endpoint <code>/api/forge/projects/demo_ecommerce/download</code>).
            </p>
          </section>

          {/* Columna derecha: resultado de generate_from_requirements */}
          <section className="space-y-3">
            <h2 className="text-lg font-semibold">
              Resultado de generate_from_requirements
            </h2>
            {!response && (
              <p className="text-sm text-slate-400">
                Aún no se ha generado nada. Pulsa “Generar backend desde
                requisitos”.
              </p>
            )}
            {response && (
              <div className="rounded-md border border-slate-800 bg-slate-900 p-3 text-xs overflow-auto max-h-80">
                <pre>{JSON.stringify(response, null, 2)}</pre>
              </div>
            )}
          </section>
        </div>

        {/* Módulos disponibles */}
        <section className="space-y-3">
          <h2 className="text-lg font-semibold">Módulos Lego disponibles</h2>
          {modules.length === 0 ? (
            <p className="text-sm text-slate-400">
              Aún no se han cargado módulos. Pulsa “Ver módulos Lego
              disponibles”.
            </p>
          ) : (
            <div className="grid md:grid-cols-3 gap-4">
              {modules.map((m) => (
                <div
                  key={m.name}
                  className="rounded-md border border-slate-800 bg-slate-900 p-3"
                >
                  <div className="text-xs text-slate-400 uppercase mb-1">
                    {m.category}
                  </div>
                  <div className="text-sm font-semibold mb-1">
                    {m.name}
                  </div>
                  {m.description && (
                    <p className="text-xs text-slate-400 mb-1 line-clamp-3">
                      {m.description}
                    </p>
                  )}
                  <div className="flex flex-wrap gap-1 mt-1">
                    {m.tags?.map((t) => (
                      <span
                        key={t}
                        className="inline-flex items-center rounded-full bg-slate-800 px-2 py-0.5 text-[10px] text-slate-300"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
