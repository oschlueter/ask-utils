#!/opt/local/bin/python

import argparse
import json
import os
import sys


class AskUtils:
    def __init__(self):
        self.data = AskUtils.load_json('skill.json')

    @staticmethod
    def load_json(fn):
        with open(fn) as f:
            return json.load(f)

    @staticmethod
    def save_json(fn, data):
        with open(fn, 'w') as f:
            json.dump(data, f, indent=True)

    def save(self):
        AskUtils.save_json('skill.json', self.data)

    def get_single_locale(self):
        locales = list(self.data['manifest']['publishingInformation']['locales'].keys())

        if len(locales) != 1:
            raise ValueError('this option only works for single-locale skills')

        return locales[0]

    def set_privacy_compliance(self, allows_purchases=False, export_compliant=True, contains_ads=False,
                               child_directed=False, personal_info=False):
        self.data['manifest']['privacyAndCompliance'] = {
            "allowsPurchases": allows_purchases,
            "isExportCompliant": export_compliant,
            "containsAds": contains_ads,
            "isChildDirected": child_directed,
            "usesPersonalInfo": personal_info
        }

    def set_icons(self, small_icon, large_icon):
        parent = self.data['manifest']['publishingInformation']['locales'][self.get_single_locale()]
        parent['smallIconUri'] = small_icon
        parent['largeIconUri'] = large_icon

    def set_keywords(self, keywords):
        parent = self.data['manifest']['publishingInformation']['locales'][self.get_single_locale()]
        parent['keywords'] = keywords

    def change_locale(self, new_locale):
        loc = self.data['manifest']['publishingInformation']['locales']

        if new_locale not in loc:
            single_locale = self.get_single_locale()

            # change key in dict
            loc[new_locale] = loc[single_locale]
            del loc[single_locale]

            # rename model file
            os.rename('models/{}.json'.format(single_locale), 'models/{}.json'.format(new_locale))

    def set_summary(self, summary):
        parent = self.data['manifest']['publishingInformation']['locales'][self.get_single_locale()]
        parent['summary'] = summary

    def set_description(self, description):
        parent = self.data['manifest']['publishingInformation']['locales'][self.get_single_locale()]
        parent['description'] = description

    def set_example_phrases(self, phrases):
        parent = self.data['manifest']['publishingInformation']['locales'][self.get_single_locale()]
        parent['examplePhrases'] = phrases

    def set_skill_name(self, skill_name):
        parent = self.data['manifest']['publishingInformation']['locales'][self.get_single_locale()]
        parent['name'] = skill_name

    def set_testing_instructions(self, testing_instructions):
        parent = self.data['manifest']['publishingInformation']
        parent['testingInstructions'] = testing_instructions

    def set_category(self, category):
        # TODO input validation
        parent = self.data['manifest']['publishingInformation']
        parent['category'] = category

    def set_invocation_name(self, invocation_name):
        single_locale = self.get_single_locale()
        fn = 'models/{}.json'.format(single_locale)

        model = AskUtils.load_json(fn)
        model['interactionModel']['languageModel']['invocationName'] = invocation_name.lower()
        AskUtils.save_json(fn, model)

    def set_language_model(self, language_model):
        single_locale = self.get_single_locale()
        fn = 'models/{}.json'.format(single_locale)

        new_lang_model = AskUtils.load_json(language_model)

        model = AskUtils.load_json(fn)
        model['interactionModel']['languageModel'] = new_lang_model['languageModel']
        AskUtils.save_json(fn, model)


if __name__ == '__main__':
    # TODO accept values for --privacy
    # TODO support multiple locales
    # TODO copy existing locale to other target locales (e.g. en-US to en-CA)
    # TODO delete locale? create backup prior to deleting
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keywords', nargs='+', help='List of keywords for the skill')
    parser.add_argument('--icons', nargs=2, help='Set URLs for small icon and large icon')
    parser.add_argument('-i', '--invocation-name', help='See ASK instructions for proper choices')
    parser.add_argument('-p', '--privacy', action='store_true', help='Sets privacy and compliance (defaults for now)')
    parser.add_argument('--change-locale', help='Changes single locale to new value')
    parser.add_argument('-s', '--summary', help='A short summary for the skill')
    parser.add_argument('-d', '--description', help='A full description for the skill')
    parser.add_argument('-e', '--example-phrases', nargs='+', help='Example phrases for the skill')
    parser.add_argument('-n', '--skill-name', help='The name of the skill (not invocation name!)')
    parser.add_argument('-t', '--testing-instructions', help='Testing instructions for the skill')
    parser.add_argument('-c', '--category', help="This skill's category")
    parser.add_argument('--language-model', help="Overwrites language model with content from provided JSON file")
    # parser.add_argument('--upload-icons', nargs=2, help='Upload small icon and large icon and set URLs in skill.json')
    # parser.add_argument('--select-category', help='Interactive selection of skill category')

    args = parser.parse_args()

    # TODO add option to specify path to skill.json
    if not os.path.isfile('skill.json'):
        print('skill.json not found')
        sys.exit(1)

    # TODO replace if statements with arguments to add_argument's action parameter
    utils = AskUtils()

    if args.privacy:
        utils.set_privacy_compliance()

    if args.icons:
        utils.set_icons(args.icons[0], args.icons[1])

    if args.keywords:
        utils.set_keywords(args.keywords)

    if args.change_locale:
        utils.change_locale(args.change_locale)

    if args.summary:
        utils.set_summary(args.summary)

    if args.description:
        utils.set_description(args.description)

    if args.example_phrases:
        utils.set_example_phrases(args.example_phrases)

    if args.skill_name:
        utils.set_skill_name(args.skill_name)

    if args.testing_instructions:
        utils.set_testing_instructions(args.testing_instructions)

    if args.category:
        utils.set_category(args.category)

    if args.invocation_name:
        utils.set_invocation_name(args.invocation_name)

    if args.language_model:
        utils.set_language_model(args.language_model)

    utils.save()
