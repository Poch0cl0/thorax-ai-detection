import { useCallback, useEffect, useRef, useState } from 'react'
import * as clinical from '../services/clinicalService'
import type { ModelOption, ScanResult } from '../types/api'
import './ScanPage.css'

export function ScanPage() {
  /* ------------------------------------------------------------------ */
  /* State                                                               */
  /* ------------------------------------------------------------------ */
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [modelType, setModelType] = useState('random_forest')
  const [modelOptions, setModelOptions] = useState<ModelOption[]>([
    {
      value: 'random_forest',
      label: 'Random Forest',
      description: 'Modelo ensemble con alta precisión',
    },
    {
      value: 'logistic_regression',
      label: 'Regresión Logística',
      description: 'Modelo lineal rápido con buena interpretabilidad',
    },
  ])
  const [result, setResult] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)

  /* ------------------------------------------------------------------ */
  /* Cargar modelos disponibles al montar                                */
  /* ------------------------------------------------------------------ */
  useEffect(() => {
    let cancelled = false
    void (async () => {
      try {
        const info = await clinical.getAvailableModels()
        if (!cancelled && info.model_options.length > 0) {
          setModelOptions(info.model_options)
          if (info.available_models.length > 0) {
            setModelType(info.available_models[0])
          }
        }
      } catch {
        /* usar opciones por defecto */
      }
    })()
    return () => { cancelled = true }
  }, [])

  /* ------------------------------------------------------------------ */
  /* Handlers de archivo                                                 */
  /* ------------------------------------------------------------------ */
  const handleFile = useCallback((f: File | null) => {
    setError(null)
    setResult(null)

    if (!f) {
      setFile(null)
      setPreview(null)
      return
    }

    // Validar tipo
    const allowed = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp']
    if (!allowed.includes(f.type)) {
      setError('Formato no soportado. Usa JPEG, PNG, BMP, TIFF o WebP.')
      return
    }

    // Validar tamaño (10 MB)
    if (f.size > 10 * 1024 * 1024) {
      setError('La imagen excede el tamaño máximo (10 MB).')
      return
    }

    setFile(f)

    // Generar preview
    const reader = new FileReader()
    reader.onload = (e) => setPreview(e.target?.result as string)
    reader.readAsDataURL(f)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragOver(false)
      const f = e.dataTransfer.files[0]
      if (f) handleFile(f)
    },
    [handleFile],
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setDragOver(false)
  }, [])

  /* ------------------------------------------------------------------ */
  /* Enviar análisis                                                     */
  /* ------------------------------------------------------------------ */
  const handleAnalyze = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const scanResult = await clinical.analyzeScan(file, modelType)
      setResult(scanResult)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al analizar la imagen')
    } finally {
      setLoading(false)
    }
  }

  /* ------------------------------------------------------------------ */
  /* Helpers de formato                                                  */
  /* ------------------------------------------------------------------ */
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const riskEmoji = (level: string) => {
    if (level === 'alto') return '🔴'
    if (level === 'moderado') return '🟡'
    return '🟢'
  }

  /* ------------------------------------------------------------------ */
  /* Render                                                              */
  /* ------------------------------------------------------------------ */
  return (
    <div>
      {/* Header */}
      <div className="scan-header">
        <h1>🔬 Análisis de Radiografía Torácica</h1>
        <p className="subtitle">
          Sube una imagen de radiografía transversal de tórax y nuestro sistema
          de inteligencia artificial analizará la presencia de posibles
          anomalías compatibles con cáncer.
        </p>
      </div>

      {/* Layout 2 columnas */}
      <div className="scan-layout">
        {/* ============= COLUMNA IZQUIERDA ============= */}
        <div className="scan-card">
          <h2>
            <span className="icon">📤</span> Subir Radiografía
          </h2>

          {/* Zona de upload */}
          <div
            className={`upload-zone${dragOver ? ' drag-over' : ''}${file ? ' has-file' : ''}`}
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') fileInputRef.current?.click()
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/bmp,image/tiff,image/webp"
              onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
            />
            {!file ? (
              <>
                <span className="upload-icon">🩻</span>
                <p className="upload-text">
                  <strong>Arrastra una imagen aquí</strong> o haz clic para
                  seleccionar
                </p>
                <p className="upload-formats">
                  JPEG, PNG, BMP, TIFF, WebP · Máx. 10 MB
                </p>
              </>
            ) : (
              <p className="upload-text">
                ✅ Imagen cargada — haz clic para cambiar
              </p>
            )}
          </div>

          {/* Preview */}
          {preview && file && (
            <div className="image-preview">
              <img src={preview} alt="Preview de radiografía" />
              <div className="file-info">
                <span>{file.name} · {formatSize(file.size)}</span>
                <button
                  type="button"
                  className="btn-remove"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleFile(null)
                  }}
                >
                  ✕ Quitar
                </button>
              </div>
            </div>
          )}

          {/* Selector de modelo */}
          <div className="model-selector">
            <label>Modelo de IA</label>
            <div className="model-options">
              {modelOptions.map((opt) => (
                <div
                  key={opt.value}
                  className={`model-option${modelType === opt.value ? ' selected' : ''}`}
                  onClick={() => setModelType(opt.value)}
                  role="radio"
                  aria-checked={modelType === opt.value}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') setModelType(opt.value)
                  }}
                >
                  <span className="model-name">{opt.label}</span>
                  <span className="model-desc">{opt.description}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Botón analizar */}
          <button
            id="btn-analyze-scan"
            type="button"
            className={`btn-analyze${loading ? ' loading' : ''}`}
            disabled={!file || loading}
            onClick={handleAnalyze}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Analizando imagen…
              </>
            ) : (
              '🔍 Analizar Radiografía'
            )}
          </button>

          {/* Error */}
          {error && <div className="scan-error">⚠️ {error}</div>}
        </div>

        {/* ============= COLUMNA DERECHA ============= */}
        <div className="scan-card">
          <h2>
            <span className="icon">📊</span> Resultados del Análisis
          </h2>

          {!result && !loading && (
            <div className="results-placeholder">
              <span className="placeholder-icon">🏥</span>
              <p>
                Sube una imagen de radiografía y selecciona un modelo para
                obtener el análisis de detección.
              </p>
            </div>
          )}

          {loading && (
            <div className="results-placeholder">
              <span className="placeholder-icon">⏳</span>
              <p>Procesando imagen con el modelo de IA…</p>
            </div>
          )}

          {result && (
            <div className="results-panel">
              {/* Predicción principal */}
              <div
                className={`prediction-main ${result.prediction === 'cancer_detected' ? 'cancer' : 'normal'}`}
              >
                <span className="prediction-icon">
                  {result.prediction === 'cancer_detected' ? '⚠️' : '✅'}
                </span>
                <div className="prediction-label">
                  {result.prediction === 'cancer_detected'
                    ? 'Anomalía Detectada'
                    : 'Sin Anomalías Significativas'}
                </div>
                <div className="prediction-confidence animate-number">
                  Confianza: {result.confidence_percent.toFixed(1)}%
                </div>
              </div>

              {/* Barras de probabilidad */}
              <div className="probability-section">
                <h3>Distribución de Probabilidad</h3>

                <div className="prob-bar-container">
                  <div className="prob-bar-label">
                    <span className="label-text">Probabilidad de cáncer</span>
                    <span className="label-value cancer">
                      {(result.probability_cancer * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="prob-bar-track">
                    <div
                      className="prob-bar-fill cancer"
                      style={{ width: `${result.probability_cancer * 100}%` }}
                    />
                  </div>
                </div>

                <div className="prob-bar-container">
                  <div className="prob-bar-label">
                    <span className="label-text">Probabilidad normal</span>
                    <span className="label-value normal">
                      {(result.probability_normal * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="prob-bar-track">
                    <div
                      className="prob-bar-fill normal"
                      style={{ width: `${result.probability_normal * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Detalles del modelo */}
              <div className="model-details">
                <div className="detail-chip">
                  <span className="chip-label">Nivel de riesgo</span>
                  <span className="chip-value">
                    <span className={`risk-badge ${result.risk_level}`}>
                      {riskEmoji(result.risk_level)} {result.risk_level.toUpperCase()}
                    </span>
                  </span>
                </div>
                <div className="detail-chip">
                  <span className="chip-label">Modelo</span>
                  <span className="chip-value">{result.model_display_name}</span>
                </div>
                <div className="detail-chip">
                  <span className="chip-label">Versión</span>
                  <span className="chip-value">{result.model_version}</span>
                </div>
                <div className="detail-chip">
                  <span className="chip-label">Confianza</span>
                  <span className="chip-value">
                    {result.confidence_percent.toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Recomendación */}
              <div className="recommendation-box">
                <h3>💡 Recomendación</h3>
                <p>{result.recommendation}</p>
              </div>

              {/* Disclaimer */}
              <div className="disclaimer-box">
                <p>{result.disclaimer}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
