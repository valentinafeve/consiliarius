import logging

import jinja2
import matplotlib.pyplot as plt
from flask import render_template

from app.model.model import Model

logger = logging.getLogger(__name__)


class ChatHandler:
    def __init__(self):
        self.model = Model()
        self.name = "User"

    def generate_html_with_waiting_status(self, telegram_chat, session_id):
        logger.info(f"Waiting to process chat with {telegram_chat['name']}")
        self.name = telegram_chat["name"]

        f = open(f"app/templates/{session_id}.html", "w+")
        f.write(render_template(f"waiting.html", name=self.name))

    def generate_html_with_scores(self, telegram_chat, session_id):
        name = telegram_chat["name"]
        logger.info(f"Processing chat with {telegram_chat['name']}")
        df = self._predict_each_line_in_file(telegram_chat)
        happiest_message = df["text"][df['scores'].idxmax()]
        saddest_message = df["text"][df['scores'].idxmin()]
        self._generate_graph_with_scores(df, session_id)
        f_session = open(f"app/templates/{session_id}.html", "w+")
        f_results = open(f"app/templates/results.html", "r")
        template = jinja2.Template(f_results.read())
        rendered = template.render(session_id=session_id,
                                   name=name,
                                   happiest_message=happiest_message,
                                   saddest_message=saddest_message)
        f_session.write(rendered)

    def _predict_each_line_in_file(self, telegram_chat):
        self.name = telegram_chat["name"]
        logging.info(f"Predicting a chat for {self.name}")
        df = self.model.generate_df_with_scores(telegram_chat)
        return df

    def _generate_graph_with_scores(self, df, session_id):
        GROUP_BATCH = len(df) // 10
        GROUP_BATCH
        group = df.groupby(lambda x: x // GROUP_BATCH)
        dates = group.nth(0).date
        plt.rcParams["figure.figsize"] = (15, 30)
        plt.xticks([i for i in range(0, len(dates))], dates, rotation='vertical')
        plt.yticks([0.356, 0.6], ["sad", "happy"])
        plt.plot(group.mean().scores)
        plt.subplots_adjust(bottom=0.8, top=1.0, left=0.1)
        plt.savefig(f"app/static/{session_id}.png")
        return None


# chat = ChatHandler()
# f = open("result.json", "r")
# telegram_chat = json.loads(f.read())
# chat.generate_html_with_scores(telegram_chat, "s")
