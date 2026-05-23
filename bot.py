import logging
import requests
import html  # Safe escaping for characters in PDFs like <, >, &
from io import BytesIO
from pypdf import PdfReader
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Predefined keywords to show as quick-select options
DEFAULT_KEYWORDS = ["insc", "scc", "fundamental", "religion"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Send me a PDF link, then either click one of the keyword buttons (including 'ALL') or type your own keyword directly."
    )

async def process_pdf_search(chat_id: int, context: ContextTypes.DEFAULT_TYPE, pdf_url: str, target_keywords: list, status_msg_id: int = None) -> None:
    display_keywords = ", ".join([kw.upper() for kw in target_keywords])
    
    # Send or edit status message
    if status_msg_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=f"⏳ Downloading and searching for '{display_keywords}'... Please wait.",
                reply_markup=None  # Clears buttons immediately
            )
        except Exception:
            new_msg = await context.bot.send_message(chat_id=chat_id, text=f"⏳ Downloading and searching for '{display_keywords}'... Please wait.")
            status_msg_id = new_msg.message_id
    else:
        new_msg = await context.bot.send_message(chat_id=chat_id, text=f"⏳ Downloading and searching for '{display_keywords}'... Please wait.")
        status_msg_id = new_msg.message_id

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
                
                matched_keywords_in_para = []
                for kw in target_keywords:
                    if kw.lower() in para_clean.lower():
                        matched_keywords_in_para.append(kw)

                if matched_keywords_in_para:
                    found_any_match = True
                    found_kw_str = ", ".join(matched_keywords_in_para)
                    
                    group_header = ""
                    if match_counter == 1 or match_counter % 2 != 0:
                        group_header = f"📦 <b>Detailed Paragraphs (Part {current_part}):</b>\n\n"
                        current_part += 1
                    
                    # Sanitize data for HTML parse_mode
                    safe_kw = html.escape(found_kw_str)
                    safe_para = html.escape(para_clean)
                    
                    # Layout using HTML containers for clean multi-line blockquotes
                    formatted_match = (
                        f"{group_header}"
                        f"📄 <b>Context Match #{match_counter}</b>\n"
                        f"🔑 Keyword: {safe_kw}\n"
                        f"<blockquote>{safe_para}</blockquote>"
                    )
                    
                    if match_counter == 1:
                        try:
                            await context.bot.delete_message(chat_id=chat_id, message_id=status_msg_id)
                        except Exception:
                            pass

                    await context.bot.send_message(chat_id=chat_id, text=formatted_match, parse_mode="HTML")
                    match_counter += 1

        if not found_any_match:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=status_msg_id,
                    text=f"🔍 Finished searching. Keywords [{display_keywords}] not found."
                )
            except Exception:
                await context.bot.send_message(chat_id=chat_id, text=f"🔍 Finished searching. Keywords [{display_keywords}] not found.")

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        try:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=status_msg_id, text="❌ Failed to complete the search. Verify the PDF is accessible.")
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text="❌ Failed to complete the search. Verify the PDF is accessible.")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("❌ Use format: `/search <url> <keyword>`")
        return
    pdf_url = context.args[0]
    keyword = " ".join(context.args[1:])
    await process_pdf_search(update.effective_chat.id, context, pdf_url, [keyword])

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    
    # User sends a link
    if text.startswith("http://") or text.startswith("https://"):
        keyboard = []
        
        # Keep URL safely tucked into session dictionary memory
        context.user_data["last_link"] = text
        
        # Minimal data layout completely evades Telegram's 64-byte payload barrier
        for kw in DEFAULT_KEYWORDS:
            keyboard.append([InlineKeyboardButton(text=kw.upper(), callback_data=f"k|{kw}")])
        
        keyboard.append([InlineKeyboardButton(text="🚨 SEARCH ALL KEYWORDS", callback_data="k|all")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📋 I detected a PDF link! Select a keyword to search below:",
            reply_markup=reply_markup
        )
        return

    # User manually inputs custom target keyword directly after passing a link
    saved_url = context.user_data.get("last_link")
    if saved_url:
        await process_pdf_search(update.effective_chat.id, context, saved_url, [text])
    else:
        await update.message.reply_text("Please send a valid PDF link first.")

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data_parts = query.data.split("|")
    if data_parts[0] == "k":
        action_keyword = data_parts[1]
        
        # Pull URL from state variables seamlessly
        pdf_url = context.user_data.get("last_link")
        
        if not pdf_url:
            await context.bot.send_message(
                chat_id=query.message.chat_id, 
                text="❌ Error: Session expired or link not found. Please send the link again."
            )
            return

        if action_keyword == "all":
            target_list = DEFAULT_KEYWORDS
        else:
            target_list = [action_keyword]

        await process_pdf_search(
            chat_id=query.message.chat_id,
            context=context,
            pdf_url=pdf_url,
            target_keywords=target_list,
            status_msg_id=query.message.message_id
        )

def main() -> None:
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("No TELEGRAM_BOT_TOKEN found.")
        return

    application = Application.builder().token(TOKEN).build()

    # Handlers array linking
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    application.add_handler(CallbackQueryHandler(handle_button_click))

    logger.info("Memory-Independent Bot Engine Active. Polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
