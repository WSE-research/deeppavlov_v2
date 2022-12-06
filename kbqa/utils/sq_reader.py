# Copyright 2017 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import pickle
from typing import List

from deeppavlov.core.common.registry import register
from deeppavlov.core.data.dataset_reader import DatasetReader


@register('sq_reader')
class SQReader(DatasetReader):
    """Class to read training datasets"""

    def read(self, data_path: str):
        if str(data_path).endswith(".pickle"):
            with open(data_path, 'rb') as f:
                dataset = pickle.load(f)
        elif str(data_path).endswith(".json"):
            with open(data_path, 'r') as f:
                dataset = json.load(f)

        return dataset


@register('rubq_reader')
class RuBQReader(SQReader):
    """Class to read RuBQ datasets"""

    def read(self, data_path: str, version: str = "2.0", question_types: List[str] = ["all"],
                   not_include_question_types: List[str] = None, num_samples: int = -1):
        dataset = super().read(data_path)
        for data_type in ["valid", "test"]:
            samples = dataset[data_type]
            samples = [sample for sample in samples if float(sample["RuBQ_version"]) <= float(version) and
                       (all([tp in sample["tags"] for tp in question_types]) or question_types == ["all"])]
            if not_include_question_types:
                samples = [sample for sample in samples if all([tp not in sample["tags"]
                           for tp in not_include_question_types])]
            samples = [self.preprocess(sample) for sample in samples]
            if num_samples > 0:
                samples = samples[:num_samples]
            dataset[data_type] = samples
        return dataset

    def preprocess(self, sample):
        question = sample.get("question_text", "")
        answers = sample.get("answers", [])
        answer_ids = [elem.get("value", "").split("/")[-1] for elem in answers]
        answer_labels = [elem.get("label", "").split("/")[-1] for elem in answers]
        query = sample.get("query", "")
        question_type = sample.get("tags", [])
        if query is None:
            query = ""
        else:
            query = query.replace("\n", " ").replace("  ", " ")
        return [[question, question_type], [answer_ids, answer_labels, query]]


@register('lcquad_reader')
class LCQuADReader(SQReader):
    """Class to read LCQuAD dataset"""

    def read(self, data_path: str, question_type: List[str] = "all",
                   not_include_question_types: List[str] = None, num_samples: int = -1):
        dataset = super().read(data_path)
        for data_type in ["valid", "test"]:
            samples = dataset[data_type]
            samples = [sample for sample in samples if (question_type == sample["query_type"]
                                                        or question_type == "all")]
            if not_include_question_types:
                samples = [sample for sample in samples
                           if sample["query_type"] not in not_include_question_types]
            samples = [self.preprocess(sample) for sample in samples]
            if num_samples > 0:
                samples = samples[:num_samples]
            dataset[data_type] = samples
        return dataset

    def preprocess(self, sample):
        question = sample.get("corrected_question", "")
        answers = sample.get("answer", [])
        query = sample.get("sparql_query", "")
        return [question, [answers, query]]
