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
    # class vars for convenience in helper methods.
    string_1 = ""
    string_2 = ""

    def get_str_count(self, word, text):
        """returns count of word/text in doc text"""
        my_regex = r"\b" + re.escape(word) + r"\b"
        return len(re.findall(my_regex, text))

    def make_df(self, dates, s1_counts, s2_counts, names):
        """makes a pandas dataframe with the given lists"""
        df = pd.DataFrame(
            list(zip(dates, names, s1_counts, s2_counts)),
            columns=["datetime", "Document Title", self.string_1, self.string_2],
        )
        df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)
        df["date"] = df["datetime"].dt.date
        df = df.drop(columns=["datetime"])
        df = df.sort_values(by="date")
        return df

    def make_graphs(self, df):
        """Uses pandas inbuilt plotting functionality to create frequency plots"""
        lines_1 = df.plot(
            y=self.string_1,
            kind="line",
            x="date",
            title='"' + self.string_1 + '" ' + ": Frequency Over Time",
            figsize=(12, 8),
        )
        fig_1 = lines_1.get_figure()
        fig_1.savefig("n-gram-graph-1.png")

        lines_2 = df.plot(
            y=self.string_2,
            kind="line",
            x="date",
            title='"' + self.string_2 + '" ' + ": Frequency Over Time",
            figsize=(12, 8),
        )
        fig_2 = lines_2.get_figure()
        fig_2.savefig("n-gram-graph-2.png")

        lines_3 = df.plot(
            kind="line",
            x="date",
            title=self.string_1 + " and " + self.string_2 + ": Frequency Over Time",
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
        doc_names = []

        def process_doc(document):
            """helper method to retrieve all relevant data from a document."""
            document_dates.append(str(document.created_at))
            doc_text = document.full_text
            doc_text = doc_text.lower()
            string_1_counts.append(self.get_str_count(self.string_1, doc_text))
            string_2_counts.append(self.get_str_count(self.string_2, doc_text))
            doc_names.append(document.title)

        # process each document in a query or list of documents
        if self.documents:
            for document in self.client.documents.list(id__in=self.documents):
                process_doc(document)

        elif self.query:
            documents = self.client.documents.search(self.query)
            for document in documents:
                process_doc(document)

        # create the pandas dataframe and sort by date.
        df = self.make_df(document_dates, string_1_counts, string_2_counts, doc_names)

        # create 3 different graphs.
        self.make_graphs(df)

        # save a csv.
        df.to_csv("n-gram-data.csv")

        # create the zipfile.
        zip_obj = ZipFile("n-gram-graphs.zip", "w")
        # Add multiple files to the zip
        zip_obj.write("n-gram-graph-1.png")
        zip_obj.write("n-gram-graph-2.png")
        zip_obj.write("n-gram-graph-3.png")
        zip_obj.write("n-gram-data.csv")

        if zip_obj.testzip() != None:
            raise IOError("Something was wrong with the zipfile!")

        zip_obj.close()

        with open("n-gram-graphs.zip", "r") as file_:
            # upload our zipfile.
            self.upload_file(file_)

        self.set_message("N-gram Graphs end!")


if __name__ == "__main__":
    NGram().main()
