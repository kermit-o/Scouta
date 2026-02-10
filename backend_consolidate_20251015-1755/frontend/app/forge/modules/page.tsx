'use client';

import { useEffect, useState } from 'react';

type ModuleSpec = {
  name: string;
  category: string;
  tags: string[];
  required_env: string[];
  description: string;
};

type ResourceField = {
  name: string;
  sqlalchemy_type: string;
  type_hint: string;
  options: string;
};

type ResourceSpec = {
  model_class_name: string;
  table_name: string;
  resource_name: string;
  resource_name_plural: string;
  fields: ResourceField[];
};

type ModuleResources = Record<string, ResourceSpec[]>;

type GenerateResultItem = {
  module: string;
  resource_name: string;
  output_dir: string;
  files: Record<string, string>;
};

type GenerateResponse = {
  module?: string; // generate_from_module
  generated?: GenerateResultItem[];
};

export default function ForgeModulesPage() {
  const [modules, setModules] = useState<ModuleSpec[]>([]);
  const [resources, setResources] = useState<ModuleResources>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedModule, setSelectedModule] = useState<string | null>(null);

  const [generateLoading, setGenerateLoading] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [generateResult, setGenerateResult] = useState<GenerateResultItem[]>(
    [],
  );

  // Carga inicial de módulos y recursos declarados en el backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [modsRes, resRes] = await Promise.all([
          fetch('/api/forge/modules'),
          fetch('/api/forge/module_resources'),
        ]);

        if (!modsRes.ok) {
          throw new Error(`modules HTTP ${modsRes.status}`);
        }
        if (!resRes.ok) {
          throw new Error(`module_resources HTTP ${resRes.status}`);
        }

        const mods = (await modsRes.json()) as ModuleSpec[];
        const resMap = (await resRes.json()) as ModuleResources;

        setModules(mods);
        setResources(resMap);

        if (mods.length > 0) {
          setSelectedModule(mods[0].name);
        }
      } catch (err: any) {
        console.error('[ForgeModulesPage] Error fetching data:', err);
        setError(err?.message ?? 'Error loading modules');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const selectedSpecs: ResourceSpec[] =
    (selectedModule && resources[selectedModule]) || [];

  const handleGenerateForSelected = async () => {
    if (!selectedModule) return;
    try {
      setGenerateLoading(true);
      setGenerateError(null);
      setGenerateResult([]);

      const res = await fetch('/api/forge/generate_from_module', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ module_name: selectedModule }),
      });

      if (!res.ok) {
        const text = await res.text();
        console.error(
          '[ForgeModulesPage] Generate error, status:',
          res.status,
          'body:',
          text,
        );
        throw new Error(`HTTP ${res.status}: ${text}`);
      }

      const data = (await res.json()) as GenerateResponse;

      const generated = data.generated ?? [];
      setGenerateResult(generated);
    } catch (err: any) {
      setGenerateError(err?.message ?? 'Error generating module backend');
    } finally {
      setGenerateLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-6xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-bold mb-2">Forge · Lego Modules</h1>
        <p className="text-sm text-slate-400 mb-6">
          Explora los módulos Lego disponibles en el backend consolidado y
          mira qué recursos backend generan (models, schemas, services,
          routers). Desde aquí también puedes disparar la generación de código
          para un módulo concreto.
        </p>

        {loading && <p className="text-sm text-slate-400">Cargando...</p>}
        {error && (
          <p className="text-sm text-red-400">
            Error cargando módulos: {error}
          </p>
        )}

        {!loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Lista de módulos */}
            <div className="md:col-span-1 space-y-3">
              <h2 className="text-sm font-semibold text-slate-200 mb-2">
                Módulos
              </h2>
              <div className="rounded-md bg-slate-900 border border-slate-700 max-h-[500px] overflow-auto text-sm">
                {modules.map((mod) => {
                  const isActive = mod.name === selectedModule;
                  return (
                    <button
                      key={mod.name}
                      type="button"
                      onClick={() => {
                        setSelectedModule(mod.name);
                        setGenerateResult([]);
                        setGenerateError(null);
                      }}
                      className={[
                        'w-full text-left px-3 py-2 border-b border-slate-800 hover:bg-slate-800',
                        isActive ? 'bg-slate-800' : '',
                      ]
                        .filter(Boolean)
                        .join(' ')}
                    >
                      <div className="text-xs uppercase text-emerald-400">
                        {mod.category}
                      </div>
                      <div className="font-medium">{mod.name}</div>
                      {mod.tags?.length > 0 && (
                        <div className="mt-1 flex flex-wrap gap-1">
                          {mod.tags.map((tag) => (
                            <span
                              key={tag}
                              className="inline-flex items-center px-2 py-0.5 rounded-full bg-slate-800 text-[10px] text-slate-300"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </button>
                  );
                })}
                {modules.length === 0 && (
                  <div className="px-3 py-2 text-xs text-slate-500">
                    No hay módulos registrados en el backend.
                  </div>
                )}
              </div>
            </div>

            {/* Detalle del módulo + generación */}
            <div className="md:col-span-2 space-y-4">
              <h2 className="text-sm font-semibold text-slate-200 mb-2">
                Detalle del módulo
              </h2>
              {!selectedModule && (
                <p className="text-sm text-slate-500">
                  Selecciona un módulo en la lista para ver sus recursos y
                  generar código.
                </p>
              )}

              {selectedModule && (
                <>
                  {(() => {
                    const mod = modules.find((m) => m.name === selectedModule);
                    if (!mod) return null;
                    return (
                      <div className="rounded-md bg-slate-900 border border-slate-700 p-3 text-sm space-y-2">
                        <div className="flex items-center justify-between gap-2">
                          <div>
                            <div>
                              <span className="font-semibold text-emerald-400">
                                Nombre:
                              </span>{' '}
                              <span>{mod.name}</span>
                            </div>
                            <div>
                              <span className="font-semibold text-emerald-400">
                                Categoría:
                              </span>{' '}
                              <span>{mod.category}</span>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={handleGenerateForSelected}
                            disabled={generateLoading}
                            className="inline-flex items-center px-3 py-1.5 rounded-md text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-900 disabled:opacity-60 disabled:cursor-not-allowed"
                          >
                            {generateLoading
                              ? 'Generando...'
                              : 'Generar backend de este módulo'}
                          </button>
                        </div>
                        {mod.required_env?.length > 0 && (
                          <div>
                            <span className="font-semibold text-emerald-400">
                              Env vars requeridas:
                            </span>{' '}
                            <span>{mod.required_env.join(', ')}</span>
                          </div>
                        )}
                        {mod.description && (
                          <div>
                            <span className="font-semibold text-emerald-400">
                              Descripción:
                            </span>{' '}
                            <span className="text-slate-300">
                              {mod.description}
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  })()}

                  {/* Recursos declarados */}
                  <div className="space-y-3">
                    <h3 className="text-xs font-semibold text-slate-300">
                      Recursos declarados para este módulo
                    </h3>
                    {selectedSpecs.length === 0 && (
                      <p className="text-xs text-slate-500">
                        Este módulo no tiene recursos declarados en el
                        registry MODULE_RESOURCES del backend (o todavía no
                        los hemos definido).
                      </p>
                    )}
                    {selectedSpecs.map((spec) => (
                      <div
                        key={spec.resource_name}
                        className="rounded-md bg-slate-900 border border-slate-700 p-3 text-xs"
                      >
                        <div>
                          <span className="font-semibold text-emerald-400">
                            Model:
                          </span>{' '}
                          {spec.model_class_name} → table:{' '}
                          {spec.table_name}
                        </div>
                        <div>
                          <span className="font-semibold text-emerald-400">
                            Resource:
                          </span>{' '}
                          {spec.resource_name} ({spec.resource_name_plural})
                        </div>
                        <div className="mt-2">
                          <span className="font-semibold text-emerald-400">
                            Fields:
                          </span>
                          <ul className="mt-1 ml-4 list-disc space-y-1">
                            {spec.fields.map((f) => (
                              <li key={f.name}>
                                <span className="text-slate-200">
                                  {f.name}
                                </span>{' '}
                                <span className="text-slate-400">
                                  ({f.sqlalchemy_type} /{' '}
                                  {f.type_hint})
                                </span>
                                {f.options && (
                                  <span className="text-slate-500">
                                    {' '}
                                    · {f.options}
                                  </span>
                                )}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Resultado de generación */}
                  <div className="space-y-2">
                    <h3 className="text-xs font-semibold text-slate-300">
                      Resultado de la última generación
                    </h3>
                    {generateError && (
                      <p className="text-xs text-red-400">
                        Error generando backend: {generateError}
                      </p>
                    )}
                    {!generateError && generateResult.length === 0 && (
                      <p className="text-xs text-slate-500">
                        Aún no has generado código para este módulo desde
                        esta pantalla.
                      </p>
                    )}
                    {generateResult.length > 0 && (
                      <div className="space-y-2 text-xs">
                        {generateResult.map((item) => (
                          <div
                            key={`${item.module}-${item.resource_name}-${item.output_dir}`}
                            className="rounded-md bg-slate-900 border border-slate-700 p-3"
                          >
                            <div>
                              <span className="font-semibold text-emerald-400">
                                Módulo:
                              </span>{' '}
                              {item.module}
                            </div>
                            <div>
                              <span className="font-semibold text-emerald-400">
                                Recurso:
                              </span>{' '}
                              {item.resource_name}
                            </div>
                            <div>
                              <span className="font-semibold text-emerald-400">
                                Output dir:
                              </span>{' '}
                              <code className="text-slate-300">
                                {item.output_dir}
                              </code>
                            </div>
                            <div className="mt-1">
                              <span className="font-semibold text-emerald-400">
                                Archivos:
                              </span>
                              <ul className="mt-1 ml-4 list-disc space-y-1">
                                {Object.entries(item.files).map(
                                  ([kind, path]) => (
                                    <li key={kind}>
                                      <span className="text-slate-200">
                                        {kind}:
                                      </span>{' '}
                                      <code className="text-slate-300">
                                        {path}
                                      </code>
                                    </li>
                                  ),
                                )}
                              </ul>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
