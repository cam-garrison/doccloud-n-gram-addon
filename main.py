"""
This addon creates n-gram graphs 
of word frequency in documents over time.
It can accept a query or a list of documents. 
"""

from documentcloud.addon import AddOn
import pandas as pd
import re
from zipfile import ZipFile


class NGram(AddOn):
    string_1 = ""
    string_2 = ""

    def get_str_count(self, word, text):
        """returns count of word/text in doc text"""
        my_regex = r"" + re.escape(word)
        return len(re.findall(my_regex, text))

    def make_df(self, dates, s1_counts, s2_counts):
        """makes a pandas dataframe with the given lists"""
        df = pd.DataFrame(
            list(zip(dates, s1_counts, s2_counts)),
            columns=["datetime", self.string_1, self.string_2],
        )
        df["datetime"] = df["datetime"].astype("datetime64")
        df["date"] = df["datetime"].dt.date
        df = df.sort_values(by="date")
        return df

    def make_graphs(self, df):
        lines_1 = df.plot(
            y=self.string_1,
            kind="line",
            x="date",
            title=self.string_1 + "Frequency Over Time",
            figsize=(12, 8),
        )

        fig_1 = lines_1.get_figure()
        fig_1.savefig("n-gram-graph-1.png")

        lines_2 = df.plot(
            y=self.string_2,
            kind="line",
            x="date",
            title=self.string_2 + "Frequency Over Time",
            figsize=(12, 8),
        )

        fig_2 = lines_2.get_figure()
        fig_2.savefig("n-gram-graph-2.png")

        lines_3 = df.plot(
            kind="line",
            x="date",
            title=self.string_1 + " " + self.string_2 + "Uploads Over Time",
            figsize=(12, 8),
        )

        fig_3 = lines_3.get_figure()
        fig_3.savefig("n-gram-graph-3.png")
        return

    def main(self):
        """The main add-on functionality goes here."""
        # fetch your add-on specific data
        string_1 = self.data.get("string1", "")
        string_2 = self.data.get("string2", "")

        self.string_1 = string_1.lower()
        self.string_2 = string_2.lower()

        document_dates = []
        string_1_counts = []
        string_2_counts = []

        # add a hello note to the first page of each selected document
        if self.documents:
            for document in self.client.documents.list(id__in=self.documents):
                document_dates.append(str(document.created_at))
                doc_text = document.full_text
                doc_text = doc_text.lower()
                string_1_counts.append(self.get_str_count(self.string_1, doc_text))
                string_2_counts.append(self.get_str_count(self.string_2, doc_text))

        elif self.query:
            documents = self.client.documents.search(self.query)
            for document in documents:
                document_dates.append(str(document.created_at))
                doc_text = document.full_text
                doc_text = doc_text.lower()
                string_1_counts.append(self.get_str_count(self.string_1, doc_text))
                string_2_counts.append(self.get_str_count(self.string_2, doc_text))

        df = self.make_df(document_dates, string_1_counts, string_2_counts)

        self.make_graphs(df)

        zipObj = ZipFile("n-gram-graphs.zip", "w")
        # Add multiple files to the zip
        zipObj.write("n-gram-graph-1.png")
        zipObj.write("n-gram-graph-2.png")
        zipObj.write("n-gram-graph-3.png")
        zipObj.close()

        with open("n-gram-graphs.zip", "w+") as file_:
            self.upload_file(file_)

        self.set_message("N-gram Graphs end!")


if __name__ == "__main__":
    NGram().main()
