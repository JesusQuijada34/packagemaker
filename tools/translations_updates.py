# -*- coding: utf-8 -*-
"""Traducciones curadas de la vigilancia de parches (Q-013, primera etapa).

Van en un módulo aparte porque ``tools/translations_curated.py`` ya es enorme y
estas claves pertenecen a una sola función (aviso de parches y commits nuevos).
El generador importa ``UPDATES_CURATED`` y lo trata igual que ``CURATED``.
"""

from __future__ import annotations

from typing import Dict

UPDATES_CURATED: Dict[str, Dict[str, str]] = {}

UPDATES_CURATED["fr"] = {
    "config.patch_check": "Signaler les correctifs et les nouveaux commits",
    "config.patch_check_hint": "Consulte api.github.com au démarrage toutes les 6 heures. Lecture seule : rien n'est téléchargé ni remplacé.",
    "updates.check_now": "Vérifier maintenant",
    "updates.title": "Correctif disponible",
    "updates.state_idle": "Pas encore vérifié",
    "updates.available": "Un nouveau commit est disponible ({sha}) : {message}",
    "updates.up_to_date": "À jour : aucun correctif en attente",
    "updates.unavailable": "Vérification impossible : {error}",
    "updates.unknown": "Impossible de déterminer votre commit ; le dernier est {sha}",
    "updates.metered": "Désactivé en mode mesuré",
}

UPDATES_CURATED["de"] = {
    "config.patch_check": "Auf Patches und neue Commits hinweisen",
    "config.patch_check_hint": "Fragt beim Start alle 6 Stunden api.github.com ab. Nur Lesen: es wird nichts geladen oder ersetzt.",
    "updates.check_now": "Jetzt prüfen",
    "updates.title": "Patch verfügbar",
    "updates.state_idle": "Noch nicht geprüft",
    "updates.available": "Ein neuer Commit ist verfügbar ({sha}): {message}",
    "updates.up_to_date": "Aktuell: keine ausstehenden Patches",
    "updates.unavailable": "Prüfung nicht möglich: {error}",
    "updates.unknown": "Ihr Commit konnte nicht ermittelt werden; der neueste ist {sha}",
    "updates.metered": "Im getakteten Modus deaktiviert",
}

UPDATES_CURATED["it"] = {
    "config.patch_check": "Avvisa di patch e nuovi commit",
    "config.patch_check_hint": "Consulta api.github.com all'avvio ogni 6 ore. Solo lettura: non scarica né sostituisce file.",
    "updates.check_now": "Controlla ora",
    "updates.title": "Patch disponibile",
    "updates.state_idle": "Non ancora verificato",
    "updates.available": "È disponibile un nuovo commit ({sha}): {message}",
    "updates.up_to_date": "Aggiornato: nessuna patch in sospeso",
    "updates.unavailable": "Impossibile verificare: {error}",
    "updates.unknown": "Impossibile determinare il tuo commit; l'ultimo è {sha}",
    "updates.metered": "Disattivato in modalità a consumo",
}

UPDATES_CURATED["pt"] = {
    "config.patch_check": "Avisar sobre patches e novos commits",
    "config.patch_check_hint": "Consulta api.github.com ao iniciar a cada 6 horas. Apenas leitura: não baixa nem substitui arquivos.",
    "updates.check_now": "Verificar agora",
    "updates.title": "Patch disponível",
    "updates.state_idle": "Ainda não verificado",
    "updates.available": "Há um novo commit ({sha}): {message}",
    "updates.up_to_date": "Atualizado: sem patches pendentes",
    "updates.unavailable": "Não foi possível verificar: {error}",
    "updates.unknown": "Não foi possível saber seu commit; o mais recente é {sha}",
    "updates.metered": "Desativado no modo de uso medido",
}

UPDATES_CURATED["nl"] = {
    "config.patch_check": "Melden bij patches en nieuwe commits",
    "config.patch_check_hint": "Vraagt bij het opstarten elke 6 uur api.github.com. Alleen lezen: er wordt niets gedownload of vervangen.",
    "updates.check_now": "Nu controleren",
    "updates.title": "Patch beschikbaar",
    "updates.state_idle": "Nog niet gecontroleerd",
    "updates.available": "Er is een nieuwe commit ({sha}): {message}",
    "updates.up_to_date": "Bijgewerkt: geen openstaande patches",
    "updates.unavailable": "Kon niet controleren: {error}",
    "updates.unknown": "Je commit kon niet worden bepaald; de nieuwste is {sha}",
    "updates.metered": "Uitgeschakeld in databesparingsmodus",
}

UPDATES_CURATED["pl"] = {
    "config.patch_check": "Powiadamiaj o poprawkach i nowych commitach",
    "config.patch_check_hint": "Odpyta api.github.com przy starcie co 6 godzin. Tylko odczyt: nic nie pobiera ani nie zastępuje.",
    "updates.check_now": "Sprawdź teraz",
    "updates.title": "Poprawka dostępna",
    "updates.state_idle": "Jeszcze nie sprawdzono",
    "updates.available": "Dostępny jest nowy commit ({sha}): {message}",
    "updates.up_to_date": "Aktualne: brak oczekujących poprawek",
    "updates.unavailable": "Nie udało się sprawdzić: {error}",
    "updates.unknown": "Nie udało się ustalić Twojego commita; najnowszy to {sha}",
    "updates.metered": "Wyłączone w trybie oszczędzania danych",
}

UPDATES_CURATED["tr"] = {
    "config.patch_check": "Yamaları ve yeni commit'leri bildir",
    "config.patch_check_hint": "Açılışta her 6 saatte bir api.github.com'u sorgular. Yalnızca okuma: hiçbir şey indirmez veya değiştirmez.",
    "updates.check_now": "Şimdi denetle",
    "updates.title": "Yama mevcut",
    "updates.state_idle": "Henüz denetlenmedi",
    "updates.available": "Yeni bir commit var ({sha}): {message}",
    "updates.up_to_date": "Güncel: bekleyen yama yok",
    "updates.unavailable": "Denetlenemedi: {error}",
    "updates.unknown": "Commit'iniz belirlenemedi; en son {sha}",
    "updates.metered": "Ölçülü kullanım modunda devre dışı",
}

UPDATES_CURATED["ru"] = {
    "config.patch_check": "Сообщать о патчах и новых коммитах",
    "config.patch_check_hint": "Запрашивает api.github.com при запуске каждые 6 часов. Только чтение: ничего не скачивается и не заменяется.",
    "updates.check_now": "Проверить сейчас",
    "updates.title": "Доступен патч",
    "updates.state_idle": "Ещё не проверено",
    "updates.available": "Доступен новый коммит ({sha}): {message}",
    "updates.up_to_date": "Актуально: ожидающих патчей нет",
    "updates.unavailable": "Не удалось проверить: {error}",
    "updates.unknown": "Не удалось определить ваш коммит; последний — {sha}",
    "updates.metered": "Отключено в режиме экономии трафика",
}

UPDATES_CURATED["ja"] = {
    "config.patch_check": "パッチと新しいコミットを通知する",
    "config.patch_check_hint": "起動時に6時間ごとに api.github.com を確認します。読み取りのみで、ダウンロードや置換は行いません。",
    "updates.check_now": "今すぐ確認",
    "updates.title": "パッチがあります",
    "updates.state_idle": "まだ確認していません",
    "updates.available": "新しいコミットがあります（{sha}）: {message}",
    "updates.up_to_date": "最新です: 保留中のパッチはありません",
    "updates.unavailable": "確認できませんでした: {error}",
    "updates.unknown": "あなたのコミットを特定できません。最新は {sha} です",
    "updates.metered": "従量制モードでは無効です",
}

UPDATES_CURATED["ko"] = {
    "config.patch_check": "패치 및 새 커밋 알림",
    "config.patch_check_hint": "시작할 때 6시간마다 api.github.com을 확인합니다. 읽기 전용이며 다운로드나 파일 교체는 하지 않습니다.",
    "updates.check_now": "지금 확인",
    "updates.title": "패치 사용 가능",
    "updates.state_idle": "아직 확인하지 않음",
    "updates.available": "새 커밋이 있습니다 ({sha}): {message}",
    "updates.up_to_date": "최신 상태: 대기 중인 패치 없음",
    "updates.unavailable": "확인할 수 없습니다: {error}",
    "updates.unknown": "현재 커밋을 확인할 수 없습니다. 최신은 {sha}입니다",
    "updates.metered": "종량제 모드에서는 사용 안 함",
}

UPDATES_CURATED["zh"] = {
    "config.patch_check": "通知补丁和新提交",
    "config.patch_check_hint": "启动时每 6 小时查询一次 api.github.com。仅读取，不下载也不替换任何文件。",
    "updates.check_now": "立即检查",
    "updates.title": "有可用补丁",
    "updates.state_idle": "尚未检查",
    "updates.available": "有新提交（{sha}）：{message}",
    "updates.up_to_date": "已是最新：没有待处理的补丁",
    "updates.unavailable": "无法检查：{error}",
    "updates.unknown": "无法确定你的提交；最新的是 {sha}",
    "updates.metered": "计量模式下已停用",
}

UPDATES_CURATED["ar"] = {
    "config.patch_check": "التنبيه إلى التصحيحات والالتزامات الجديدة",
    "config.patch_check_hint": "يفحص api.github.com عند بدء التشغيل كل 6 ساعات. قراءة فقط: لا يُنزّل ولا يستبدل أي ملف.",
    "updates.check_now": "تحقق الآن",
    "updates.title": "تصحيح متاح",
    "updates.state_idle": "لم يتم الفحص بعد",
    "updates.available": "يوجد التزام جديد ({sha}): {message}",
    "updates.up_to_date": "محدَّث: لا توجد تصحيحات معلّقة",
    "updates.unavailable": "تعذّر الفحص: {error}",
    "updates.unknown": "تعذّر تحديد التزام الخاص بك؛ الأحدث هو {sha}",
    "updates.metered": "معطّل في وضع الاستخدام المقنَّن",
}
