import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  EmbedBuilder,
} from "discord.js";

const MAX_CONTENT_LENGTH = 2000;
const MAX_EMBED_DESCRIPTION = 4096;

export function buildActionRows(buttonsData) {
  if (!buttonsData || !buttonsData.length) return [];

  const rows = [];
  for (const buttonRow of buttonsData) {
    const row = new ActionRowBuilder();
    for (const btn of buttonRow.slice(0, 5)) {
      const builder = new ButtonBuilder()
        .setLabel(btn.label.slice(0, 80))
        .setStyle(
          btn.action === "url"
            ? ButtonStyle.Link
            : btn.style === "danger"
              ? ButtonStyle.Danger
              : btn.style === "secondary"
                ? ButtonStyle.Secondary
                : btn.style === "success"
                  ? ButtonStyle.Success
                  : ButtonStyle.Primary
        );

      if (btn.action === "url") {
        builder.setURL(btn.value);
      } else {
        builder.setCustomId(btn.value);
      }

      row.addComponents(builder);
    }
    rows.push(row);
  }
  return rows;
}

export async function sendDiscordReply(message, data) {
  const content = data.reply_text || "";
  const components = buildActionRows(data.reply_markup?.buttons);

  if (content.length <= MAX_CONTENT_LENGTH) {
    return await message.reply({
      content,
      components,
      allowedMentions: { repliedUser: false },
    });
  }

  const embed = new EmbedBuilder()
    .setDescription(content.slice(0, MAX_EMBED_DESCRIPTION))
    .setColor(0x1e90ff);

  const remaining = content.slice(MAX_EMBED_DESCRIPTION);
  const reply = await message.reply({
    embeds: [embed],
    components,
    allowedMentions: { repliedUser: false },
  });

  if (remaining) {
    let chunk = remaining;
    while (chunk.length > 0) {
      const slice = chunk.slice(0, MAX_CONTENT_LENGTH);
      chunk = chunk.slice(MAX_CONTENT_LENGTH);
      await message.channel.send({
        content: `-# *(kontynuacja)*\n${slice}`.slice(0, MAX_CONTENT_LENGTH),
        allowedMentions: { parse: [] },
      });
    }
  }

  return reply;
}