ANNOUNCEMENT = """
⏰ Palestras Relâmpago começando em **{{ waiting_time }} : 00**
"""


NEW_LIGHTNING_TALK = """
⚡️⚡️⚡️ **Palestras Relâmpago** ⚡️⚡️⚡️

TODO: Texto sobre palestras relâmpago
TODO: Instruções de como vai funcionar no discord/streamyard
TODO: Instruções de como participar
"""


NOT_ACTIVE_LIGHTNING_TALK = """
⚡️⚡️⚡️ **Palestras Relâmpago** ⚡️⚡️⚡️

TODO: Texto sobre palestras relâmpago
TODO: Instruções de como vai funcionar no discord/streamyard
TODO: Instruções de como participar

Aguardando lista de chamada!
"""


LIGHTNING_TALK_IN_PROGRESS = """
⚡️⚡️⚡️ **Palestras Relâmpago** ⚡️⚡️⚡️

TODO: Texto sobre palestras relâmpago
TODO: Instruções de como vai funcionar no discord/streamyard
TODO: Instruções de como participar

Inscrições:
{%- for speaker in speakers %}
- <@{{ speaker }}>
{%- endfor %}
"""


LIGHTNING_TALK_SPEAKERS_ORDER = """
⚡️⚡️⚡️ **Palestras Relâmpago** ⚡️⚡️⚡️

TODO: Texto sobre palestras relâmpago
TODO: Instruções de como vai funcionar no discord/streamyard
TODO: Instruções de como participar

Inscrições:
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
