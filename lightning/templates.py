ANNOUNCEMENT = """
⏰ Palestras Relâmpago começando em **{{ waiting_time }} : 00**
"""

BASE_MAIN_MESSAGE = """
⚡️⚡️⚡️ **Palestras Relâmpago** ⚡️⚡️⚡️

Palestras Relâmpago é uma seção do evento em que qualquer pessoa pode fazer uma apresentação, sobre qualquer assunto, em **no máximo 5 minutos**.

Lembrando que Código de Conduta também se aplica as palestras relâmpago! Se você tiver alguma dúvida, converse com o time de resposta do @CDC ou com a @Organização.

**Legal! Mas como funciona aqui no Discord?**
- Após o encerramento das inscrições, vou embaralhar a lista de pessoas que querem participar e mandar aqui nesse canal a ordem de chamada. Todos os inscritos receberão uma notificação quando a lista for atualizada.
- Alguns minutos antes das palestras relâmpago começarem, os convites serão enviados por mim no privado, aqui no Discord. E caso aconteça alguma desistência, os convites continuarão sendo enviados para as próximas pessoas da lista de chamada.

**Show!! Quer participar, o que eu tenho que fazer?**
Para se inscrever, basta clicar no emoji ☝️ abaixo que o seu nome aparecerá na lista.
"""


NEW_LIGHTNING_TALK = BASE_MAIN_MESSAGE


NOT_ACTIVE_LIGHTNING_TALK = BASE_MAIN_MESSAGE + """
🥁 **Aguardando lista de chamada!** 🥁
"""


LIGHTNING_TALK_IN_PROGRESS = BASE_MAIN_MESSAGE + """
**Inscrições**:
{%- for speaker in speakers %}
- <@{{ speaker }}>
{%- endfor %}
"""


LIGHTNING_TALK_SPEAKERS_ORDER = BASE_MAIN_MESSAGE + """
**Ordem de chamada**:
{%- for speaker, data in speakers.items() %}
{%- if data.invited and not data.confirmed %}
⏰ <@{{ speaker }}>
{%- elif data.invited and data.confirmed %}
✅ <@{{ speaker }}>
{%- else %}
<@{{ speaker }}>
{%- endif %}
{%- endfor %}
"""

INVITE = """
Olá {{ speaker }}! Acesse a url abaixo para participar da palestra relâmpago:

**{{ link }}**

Boa apresentação! 🎉
"""