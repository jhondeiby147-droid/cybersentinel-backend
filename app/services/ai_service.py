import re
from transformers import pipeline

class AIService:
    def __init__(self):
        
        # 1. Pipeline de Clasificación (El cerebro que sí funciona)
        self.classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
        
        # 2. Pipeline de NER
        self.ner_engine = pipeline("ner", model="Babelscape/wikineural-multilingual-ner", aggregation_strategy="simple") # type: ignore
        

    def extract_hard_entities(self, text: str):
        entities = []
        ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
        for ip in ips:
            entities.append({"entity": ip, "category": "IP_ADDRESS", "start": text.find(ip), "end": text.find(ip)+len(ip)})
        
        ports = re.findall(r'(?i)port[:\s]*(\d+)', text)
        for port in ports:
            entities.append({"entity": port, "category": "PORT", "start": text.find(port), "end": text.find(port)+len(port)})
        
        return entities

    def analyze(self, text: str):
        # 1. CLASIFICACIÓN EXACTA
        labels = ["Baja", "Media", "Alta", "Crítica", "No técnico"]
        class_result = self.classifier(
            text, 
            candidate_labels=labels,
            hypothesis_template="Este texto de ciberseguridad es de categoría {}."
        )
        
        severity = class_result['labels'][0]
        score = class_result['scores'][0]

        if severity == "No técnico" or score < 0.25:
            return {
                "severity": "Informativa",
                "confidence_score": round(score, 2),
                "entities": [],
                "summary": "ENTRADA NO VÁLIDA: El texto no contiene patrones de logs técnicos o eventos de seguridad procesables."
            }

        # 2. EXTRACCIÓN HÍBRIDA
        hard_entities = self.extract_hard_entities(text)
        ner_results = self.ner_engine(text)
        ai_entities = [
            {"entity": e['word'], "category": e['entity_group'], "start": e['start'], "end": e['end']} 
            for e in ner_results
        ]
        
        all_entities = hard_entities + [e for e in ai_entities if e['entity'] not in [h['entity'] for h in hard_entities]]

        # 3. GENERACIÓN DE RESUMEN DETERMINISTA (Adiós, BBC)
        ips_encontradas = [e['entity'] for e in all_entities if e['category'] == 'IP_ADDRESS']
        puertos_encontrados = [e['entity'] for e in all_entities if e['category'] == 'PORT']
        
        ip_str = ips_encontradas[0] if ips_encontradas else "origen no identificado"
        port_str = puertos_encontrados[0] if puertos_encontrados else "puerto no especificado"

        if severity in ["Crítica", "Alta"]:
            summary_text = f"ALERTA DE SEGURIDAD: Se ha detectado un evento de severidad {severity}. " \
                           f"El incidente se originó desde la IP {ip_str} " \
                           f"afectando potencialmente el {port_str}. Se recomienda bloqueo inmediato y auditoría."
        else:
            summary_text = f"ANÁLISIS COMPLETADO: Actividad de severidad {severity} detectada. " \
                           f"Entidades vinculadas incluyen la IP {ip_str}. " \
                           f"Mantener monitoreo preventivo en los registros."

        return {
            "severity": severity,
            "confidence_score": round(score, 2),
            "entities": all_entities,
            "summary": summary_text
        }

ai_engine = AIService()