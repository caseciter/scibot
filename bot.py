async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    
    # Check if the user sent a valid link
    if text.startswith("http://") or text.startswith("https://"):
        keyboard = []
        
        # Save full link safely in memory storage attached to this user session
        context.user_data["last_link"] = text
        
        # Now callback_data stays under 10 bytes! No risk of breaking Telegram's 64-byte limit.
        for kw in DEFAULT_KEYWORDS:
            keyboard.append([InlineKeyboardButton(text=kw.upper(), callback_data=f"k|{kw}")])
        
        keyboard.append([InlineKeyboardButton(text="🚨 SEARCH ALL KEYWORDS", callback_data="k|all")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📋 I detected a PDF link! Select a keyword to search below:",
            reply_markup=reply_markup
        )
        return

    # Fallback: User manually typed a custom keyword straight into chat window
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
        
        # Retrieve the target URL safely from our runtime cache
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
