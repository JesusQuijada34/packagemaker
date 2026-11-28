# -*- coding: utf-8 -*-
"""Traducciones curadas de la tarjeta AIDE de Configuración (Q-029).

Viven aparte por la misma razón que ``translations_updates``: son claves de una
sola función y ``tools/translations_curated.py`` ya es enorme. El generador
importa ``AIDE_CURATED`` y lo trata igual que ``CURATED``.
"""

from __future__ import annotations

from typing import Dict

AIDE_CURATED: Dict[str, Dict[str, str]] = {}

AIDE_CURATED["fr"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "Fournisseur et identifiants de l'assistant",
    "config.aide_provider": "Fournisseur",
    "config.aide_endpoint": "URL du point de terminaison",
    "config.aide_model": "Modèle",
    "config.aide_api_key": "Clé d'API",
    "config.aide_key_saved": "Clé enregistrée ; saisissez-en une nouvelle pour la remplacer",
    "config.aide_key_missing": "Aucune clé enregistrée",
    "config.aide_send_context": "Joindre le contexte du projet (nettoyé)",
    "config.aide_hint": "La clé est stockée dans data/pm.data et n'est envoyée qu'au point de terminaison indiqué. Rien ne quitte la machine sans cette configuration.",
    "aide.api_key_saved": "Clé enregistrée ; saisissez-en une nouvelle pour la remplacer",
}

AIDE_CURATED["de"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "Anbieter und Zugangsdaten des Assistenten",
    "config.aide_provider": "Anbieter",
    "config.aide_endpoint": "Endpunkt-URL",
    "config.aide_model": "Modell",
    "config.aide_api_key": "API-Schlüssel",
    "config.aide_key_saved": "Schlüssel gespeichert; zum Ersetzen einen neuen eingeben",
    "config.aide_key_missing": "Kein Schlüssel gespeichert",
    "config.aide_send_context": "Projektkontext anhängen (bereinigt)",
    "config.aide_hint": "Der Schlüssel liegt in data/pm.data und wird nur an den angegebenen Endpunkt gesendet. Ohne diese Einrichtung verlässt nichts den Rechner.",
    "aide.api_key_saved": "Schlüssel gespeichert; zum Ersetzen einen neuen eingeben",
}

AIDE_CURATED["it"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "Provider e credenziali dell'assistente",
    "config.aide_provider": "Fornitore",
    "config.aide_endpoint": "URL dell'endpoint",
    "config.aide_model": "Modello",
    "config.aide_api_key": "Chiave API",
    "config.aide_key_saved": "Chiave salvata; scrivine una nuova per sostituirla",
    "config.aide_key_missing": "Nessuna chiave salvata",
    "config.aide_send_context": "Allega il contesto del progetto (ripulito)",
    "config.aide_hint": "La chiave è salvata in data/pm.data e viene inviata solo all'endpoint indicato. Nulla esce dal computer senza questa configurazione.",
    "aide.api_key_saved": "Chiave salvata; scrivine una nuova per sostituirla",
}

AIDE_CURATED["pt"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "Provedor e credenciais do assistente",
    "config.aide_provider": "Provedor",
    "config.aide_endpoint": "URL do endpoint",
    "config.aide_model": "Modelo",
    "config.aide_api_key": "Chave de API",
    "config.aide_key_saved": "Chave salva; digite outra para substituí-la",
    "config.aide_key_missing": "Nenhuma chave salva",
    "config.aide_send_context": "Anexar contexto do projeto (saneado)",
    "config.aide_hint": "A chave fica em data/pm.data e só é enviada ao endpoint indicado. Nada sai do computador sem esta configuração.",
    "aide.api_key_saved": "Chave salva; digite outra para substituí-la",
}

AIDE_CURATED["nl"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "Provider en inloggegevens van de assistent",
    "config.aide_provider": "Aanbieder",
    "config.aide_endpoint": "Endpoint-URL",
    "config.aide_model": "Model",
    "config.aide_api_key": "API-sleutel",
    "config.aide_key_saved": "Sleutel opgeslagen; typ een nieuwe om hem te vervangen",
    "config.aide_key_missing": "Geen sleutel opgeslagen",
    "config.aide_send_context": "Projectcontext meesturen (opgeschoond)",
    "config.aide_hint": "De sleutel staat in data/pm.data en wordt alleen naar het opgegeven endpoint gestuurd. Zonder deze instelling verlaat niets de computer.",
    "aide.api_key_saved": "Sleutel opgeslagen; typ een nieuwe om hem te vervangen",
}

AIDE_CURATED["pl"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "Dostawca i dane logowania asystenta",
    "config.aide_provider": "Dostawca",
    "config.aide_endpoint": "Adres URL punktu końcowego",
    "config.aide_model": "Model",
    "config.aide_api_key": "Klucz API",
    "config.aide_key_saved": "Klucz zapisany; wpisz nowy, aby go zastąpić",
    "config.aide_key_missing": "Brak zapisanego klucza",
    "config.aide_send_context": "Dołącz kontekst projektu (oczyszczony)",
    "config.aide_hint": "Klucz jest przechowywany w data/pm.data i wysyłany tylko do wskazanego punktu końcowego. Bez tej konfiguracji nic nie opuszcza komputera.",
    "aide.api_key_saved": "Klucz zapisany; wpisz nowy, aby go zastąpić",
}

AIDE_CURATED["ru"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "Провайдер и учётные данные помощника",
    "config.aide_provider": "Провайдер",
    "config.aide_endpoint": "URL конечной точки",
    "config.aide_model": "Модель",
    "config.aide_api_key": "Ключ API",
    "config.aide_key_saved": "Ключ сохранён; введите новый, чтобы заменить его",
    "config.aide_key_missing": "Ключ не сохранён",
    "config.aide_send_context": "Прикреплять контекст проекта (очищенный)",
    "config.aide_hint": "Ключ хранится в data/pm.data и отправляется только на указанную конечную точку. Без этой настройки данные не покидают компьютер.",
    "aide.api_key_saved": "Ключ сохранён; введите новый, чтобы заменить его",
}

AIDE_CURATED["tr"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "Asistan sağlayıcısı ve kimlik bilgileri",
    "config.aide_provider": "Sağlayıcı",
    "config.aide_endpoint": "Uç nokta URL'si",
    "config.aide_model": "Model",
    "config.aide_api_key": "API anahtarı",
    "config.aide_key_saved": "Anahtar kaydedildi; değiştirmek için yenisini yazın",
    "config.aide_key_missing": "Kayıtlı anahtar yok",
    "config.aide_send_context": "Proje bağlamını ekle (temizlenmiş)",
    "config.aide_hint": "Anahtar data/pm.data içinde saklanır ve yalnızca belirttiğiniz uç noktaya gönderilir. Bu ayar olmadan hiçbir veri bilgisayardan çıkmaz.",
    "aide.api_key_saved": "Anahtar kaydedildi; değiştirmek için yenisini yazın",
}

AIDE_CURATED["ar"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "مزوّد المساعد وبيانات اعتماده",
    "config.aide_provider": "المزوّد",
    "config.aide_endpoint": "عنوان نقطة النهاية",
    "config.aide_model": "الطراز",
    "config.aide_api_key": "مفتاح API",
    "config.aide_key_saved": "المفتاح محفوظ؛ اكتب مفتاحًا جديدًا لاستبداله",
    "config.aide_key_missing": "لا يوجد مفتاح محفوظ",
    "config.aide_send_context": "إرفاق سياق المشروع (بعد التنقية)",
    "config.aide_hint": "يُحفظ المفتاح في data/pm.data ويُرسل فقط إلى نقطة النهاية التي تحددها. لا يغادر أي شيء الجهاز دون هذا الإعداد.",
    "aide.api_key_saved": "المفتاح محفوظ؛ اكتب مفتاحًا جديدًا لاستبداله",
}

AIDE_CURATED["ja"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "アシスタントのプロバイダーと認証情報",
    "config.aide_provider": "プロバイダー",
    "config.aide_endpoint": "エンドポイント URL",
    "config.aide_model": "モデル",
    "config.aide_api_key": "API キー",
    "config.aide_key_saved": "キーは保存済みです。変更するには新しいキーを入力してください",
    "config.aide_key_missing": "保存されたキーはありません",
    "config.aide_send_context": "プロジェクトのコンテキストを添付（サニタイズ済み）",
    "config.aide_hint": "キーは data/pm.data に保存され、指定したエンドポイントにのみ送信されます。この設定がない限り、データがこの端末から出ることはありません。",
    "aide.api_key_saved": "キーは保存済みです。変更するには新しいキーを入力してください",
}

AIDE_CURATED["ko"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "어시스턴트 공급자 및 자격 증명",
    "config.aide_provider": "공급자",
    "config.aide_endpoint": "엔드포인트 URL",
    "config.aide_model": "모델",
    "config.aide_api_key": "API 키",
    "config.aide_key_saved": "키가 저장되었습니다. 바꾸려면 새 키를 입력하세요",
    "config.aide_key_missing": "저장된 키 없음",
    "config.aide_send_context": "프로젝트 컨텍스트 첨부(정리됨)",
    "config.aide_hint": "키는 data/pm.data에 저장되며 지정한 엔드포인트로만 전송됩니다. 이 설정이 없으면 어떤 데이터도 이 컴퓨터를 떠나지 않습니다.",
    "aide.api_key_saved": "키가 저장되었습니다. 바꾸려면 새 키를 입력하세요",
}

AIDE_CURATED["zh"] = {
    "config.section_aide": "AIDE",
    "config.section_aide_hint": "助手服务商与凭据",
    "config.aide_provider": "服务商",
    "config.aide_endpoint": "端点 URL",
    "config.aide_model": "模型",
    "config.aide_api_key": "API 密钥",
    "config.aide_key_saved": "密钥已保存；输入新的密钥可替换",
    "config.aide_key_missing": "尚未保存密钥",
    "config.aide_send_context": "附加项目上下文（已清理）",
    "config.aide_hint": "密钥保存在 data/pm.data 中，只会发送到你填写的端点。没有这项设置，任何数据都不会离开本机。",
    "aide.api_key_saved": "密钥已保存；输入新的密钥可替换",
}
