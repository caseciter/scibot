import logging
import requests
import html  # Safe escaping for characters in PDFs like <, >, &
from io import BytesIO
from pypdf import PdfReader
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Predefined keywords that the bot will ALWAYS search for automatically
DEFAULT_KEYWORDS = ["insc", "scc", "fundamental", "religion"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Simply paste a PDF link into this chat, and I will automatically scan it for all predefined keywords."
    )

async def process_pdf_search(chat_id: int, context: ContextTypes.DEFAULT_TYPE, pdf_url: str, target_keywords: list) -> None:
    display_keywords = ", ".join([kw.upper() for kw in target_keywords])
    
    # Send initial progress status tracker
    status_msg = await context.bot.send_message(
        chat_id=chat_id, 
        text=f"⏳ Downloading and automatically searching for: <b>{display_keywords}</b>... Please wait.",
        parse_mode="HTML"
    )

    try:
        response = requests.get(pdf_url, timeout=15)
        response.raise_for_status()
        
        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)
        
        match_counter = 1
        found_any_match = False
        current_part = 1 

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
                
            paragraphs = text.split("\n\n")
            for para in paragraphs:
                para_clean = para.strip()
                if not para_clean:
                    continue
                
                # Identify which tracking keywords are embedded inside this paragraph
                matched_keywords_in_para = []
                for kw in target_keywords:
                    if kw.lower() in para_clean.lower():
                        matched_keywords_in_para.append(kw)

                if matched_keywords_in_para:
                    found_any_match = True
                    found_kw_str = ", ".join(matched_keywords_in_para)
                    
                    # Generates structural group header parts split across multi-message payloads
                    group_header = ""
                    if match_counter == 1 or match_counter % 2 != 0:
                        group_header = f"📦 <b>Detailed Paragraphs (Part {current_part}):</b>\n\n"
                        current_part += 1
                    
                    # Sanitize all string injection tokens to protect HTML parsing engine
                    safe_kw = html.escape(found_kw_str)
                    safe_para = html.escape(para_clean)
                    
                    formatted_match = (
                        f"{group_header}"
                        f"📄 <b>Context Match #{match_counter} (Page {page_num})</b>\n"
                        f"🔑 Keyword: {safe_kw}\n"
                        f"<blockquote>{safe_para}</blockquote>"
                    )
                    
                    # Delete the loading placeholder when the very first match delivers
                    if match_counter == 1:
                        try:
                            await context.bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
                        except Exception:
                            pass

                    await context.bot.send_message(chat_id=chat_id, text=formatted_match, parse_mode="HTML")
                    match_counter += 1

        if not found_any_match:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=status_msg.message_id,
                    text=f"🔍 Finished automated search. None of the keywords [{display_keywords}] were found inside the document."
                )
            except Exception:
                await context.bot.send_message(chat_id=chat_id, text=f"🔍 Finished automated search. Keywords not found.")

    except Exception as e:
        logger.error(f"Error processing automated PDF search: {e}")
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id, 
                message_id=status_msg.message_id, 
                text="❌ Failed to complete the processing search routine. Make sure the link points to a readable, unencrypted PDF."
            )
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text="❌ Failed to complete the automated search configuration.")

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    
    # If the user drops a link, run the search across the full keyword list instantly
    if text.startswith("http://") or text.startswith("https://"):
        await process_pdf_search(
            chat_id=update.effective_chat.id, 
            context=context, 
            pdf_url=text, 
            target_keywords=DEFAULT_KEYWORDS
        )
    else:
        await update.message.reply_text("Please paste a valid direct link to a PDF document (starting with http/https).")

def main() -> None:
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment configurations.")
        return

    application = Application.builder().token(TOKEN).build()

    # Stripped away CallbackQueryHandlers since buttons are no longer needed
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    logger.info("Automated PDF Scraper Engine Online. Polling updates...")
    application.run_polling()

if __name__ == "__main__":
    main()
