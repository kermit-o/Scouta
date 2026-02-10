"""
Trend Scanner - Detecta tendencias para posts automáticos
"""
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from app.services.deepseek_client import DeepSeekClient


class TrendScanner:
    """Escanea y analiza tendencias para generar posts"""
    
    def __init__(self, deepseek_client: Optional[DeepSeekClient] = None):
        self.deepseek = deepseek_client or DeepSeekClient()
    
    def get_current_trends(self) -> List[Dict[str, Any]]:
        """
        Obtiene tendencias actuales (mock por ahora, luego integración real)
        """
        # TODO: Integrar con APIs reales: NewsAPI, Reddit, Twitter, Google Trends
        return [
            {
                "id": "trend_1",
                "title": "Super Bowl 2026: Predictions and Controversies",
                "category": "sports",
                "heat": 95,
                "keywords": ["super bowl", "nfl", "predictions", "controversy"],
                "source": "sports_news",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "id": "trend_2",
                "title": "AI Regulation: How Governments Are Responding",
                "category": "technology",
                "heat": 88,
                "keywords": ["ai", "regulation", "government", "ethics"],
                "source": "tech_news",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "id": "trend_3",
                "title": "Climate Change: Latest Scientific Breakthroughs",
                "category": "science",
                "heat": 82,
                "keywords": ["climate", "science", "breakthrough", "environment"],
                "source": "science_news",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "id": "trend_4",
                "title": "Philosophy in the Age of AI: What Does It Mean to Be Human?",
                "category": "philosophy",
                "heat": 78,
                "keywords": ["philosophy", "ai", "humanity", "ethics"],
                "source": "academic",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    
    def generate_post_from_trend(self, trend: Dict[str, Any]) -> Dict[str, Any]:
        """
        Usa DeepSeek para convertir una tendencia en un post completo
        """
        if not self.deepseek.api_key:
            # Fallback si no hay API key
            return self._generate_fallback_post(trend)
        
        prompt = f"""
        TENDENCIA: {trend['title']}
        Categoría: {trend['category']}
        Keywords: {', '.join(trend['keywords'])}
        
        Genera un post de blog completo sobre esta tendencia.
        
        Formato de respuesta JSON:
        {{
            "title": "Título atractivo y clickeable",
            "content": "Contenido completo en Markdown (5-7 párrafos)",
            "excerpt": "Resumen de 2-3 líneas para preview",
            "tags": ["tag1", "tag2", "tag3"],
            "tone": "analytical|controversial|informative|opinionated",
            "engagement_hooks": ["pregunta1", "pregunta2"]
        }}
        
        El contenido debe ser:
        1. Bien investigado (aunque inventado)
        2. Con ángulo interesante/único
        3. Con llamados a la acción para comentarios
        4. Apropiado para blog profesional
        """
        
        try:
            response = self.deepseek.chat(
                system="Eres un blogger profesional experto en crear contenido viral.",
                user=prompt
            )
            
            # Parsear respuesta
            import json
            post_data = json.loads(response)
            post_data["trend_source"] = trend
            post_data["generated_at"] = datetime.utcnow().isoformat()
            
            return post_data
            
        except Exception as e:
            print(f"Error generando post: {e}")
            return self._generate_fallback_post(trend)
    
    def _generate_fallback_post(self, trend: Dict[str, Any]) -> Dict[str, Any]:
        """Genera post básico si falla la IA"""
        return {
            "title": f"Análisis: {trend['title']}",
            "content": f"""
# {trend['title']}

Este es un análisis automático de la tendencia actual sobre **{trend['title']}**.

## Contexto
La tendencia '{trend['title']}' está ganando atención en {trend['source']}.

## Impacto
Este tema tiene implicaciones importantes para {trend['category']}.

## Perspectivas
1. Primera perspectiva interesante
2. Segunda perspectiva controvertida  
3. Tercera perspectiva futura

## Conclusión
Un tema relevante que merece discusión.

¿Qué opinas sobre {trend['keywords'][0]}?
            """.strip(),
            "excerpt": f"Análisis de la tendencia: {trend['title']}",
            "tags": trend['keywords'][:3],
            "tone": "informative",
            "engagement_hooks": [
                f"¿Qué opinas sobre {trend['keywords'][0]}?",
                "¿Estás de acuerdo con esta tendencia?"
            ],
            "trend_source": trend,
            "generated_at": datetime.utcnow().isoformat()
        }


# Ejemplo de uso
if __name__ == "__main__":
    scanner = TrendScanner()
    trends = scanner.get_current_trends()
    print(f"Encontradas {len(trends)} tendencias")
    
    if trends:
        post = scanner.generate_post_from_trend(trends[0])
        print(f"Post generado: {post['title']}")
