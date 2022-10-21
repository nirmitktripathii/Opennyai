import collections
import math
import re



def _postprocess(inference_output,rr_output):
    lawbriefs_summary_map = {1: "facts", 2: "facts", 3: "arguments_petitioner", 4: "arguments_respondent",
                             5: "issue", 6: "ANALYSIS", 7: 'ANALYSIS',
                             8: 'ANALYSIS', 9: 'ANALYSIS', 10: 'ANALYSIS',
                             11: 'decision'}  ##### keys are baseline rhetorical roles and values are LawBriefs roles.
    final_categories = {'facts': 'facts', 'issue': 'issue',
                        'arguments_petitioner': 'arguments',
                        'arguments_respondent': 'arguments',
                        'ANALYSIS': 'ANALYSIS',
                        'decision': 'decision'}  ### these are the predicted sumarry sections
    additional_mandatory_categories = ['issue', 'decision']

    # def _process_sentences_with_scores_and_add_percentile_ranks(output_inference, text_summary):
    #     temp = copy.deepcopy(output_inference)
    #     f_name = list(temp.keys())[0]
    #     sent_scores_list = temp[f_name]
    #     for sent_dict in sent_scores_list:
    #         sent_dict['sent_rhetorical_role'] = lawbriefs_summary_map[sent_dict['sent_rhetorical_role']].upper()
    #         if sent_dict['sent_txt'] in text_summary:
    #             sent_dict['sent_label'] = 1
    #
    #     df = pd.DataFrame(sent_scores_list)
    #     df['Percentile_Rank'] = df.sent_score.rank(pct=True)
    #     return df.to_dict('records')

    def get_adaptive_summary_sent_percent(sent_cnt):
        ######## get the summary sentence percentage to keep in output based in input sentence cnt. The values are found by piecewise linear regression
        if sent_cnt <= 77:
            const = 40.5421
            slope = -0.2444
        elif sent_cnt <= 122:
            const = 29.5264
            slope = -0.1013
        else:
            const = 17.8994
            slope = - 0.006
        summary_sent_precent = slope * sent_cnt + const
        return summary_sent_precent

    # def create_concatenated_summaries(file_chunk_sent_scores, use_adaptive_summary_sent_percent=True,
    #                                   summary_sent_precent=30, use_rhetorical_roles=True,
    #                                   seperate_summary_for_each_rr=True,
    #                                   add_additional_mandatory_roles_to_summary=False):
    #     predicted_rr_summaries = []
    #     #### this function accepts the sentence scores and returns predicted summary
    #     for file_name, sent_list_all in file_chunk_sent_scores.items():
    #         ####### remove sentences without single alphabet
    #         sent_list = [sent for sent in sent_list_all if re.search('[a-zA-Z]', sent['sent_txt'])]
    #         if use_adaptive_summary_sent_percent:
    #             summary_sent_precent = get_adaptive_summary_sent_percent(len(sent_list))
    #         else:
    #             summary_sent_precent = summary_sent_precent
    #
    #         if use_rhetorical_roles and seperate_summary_for_each_rr:
    #             # ######## take top N sentences for each rhetorical role
    #             file_rr_sents = {}  ##### keys are rhetorical roles and values are dict of {'sentences':[],'token_cnt':100}
    #             for sent_dict in sent_list:
    #                 sent_token_cnt = len(sent_dict['sent_txt'].split())
    #                 sent_rr = lawbriefs_summary_map[sent_dict['sent_rhetorical_role']]
    #                 if file_rr_sents.get(sent_rr) is None:
    #                     file_rr_sents[sent_rr] = {'sentences': [sent_dict], 'token_cnt': sent_token_cnt}
    #                 else:
    #                     file_rr_sents[sent_rr]['sentences'].append(sent_dict)
    #                     file_rr_sents[sent_rr]['token_cnt'] += sent_token_cnt
    #
    #             min_token_cnt_per_rr = 50  ######## if original text for a rhetorical role is below this then it is not summarized.
    #             selected_sent_list = []
    #             for rr, sentences_dict in file_rr_sents.items():
    #                 if sentences_dict['token_cnt'] <= min_token_cnt_per_rr or rr in additional_mandatory_categories:
    #                     selected_sent_list.extend(sentences_dict['sentences'])
    #                 else:
    #                     rr_sorted_sent_list = sorted(sentences_dict['sentences'], key=lambda x: x['sent_score'],
    #                                                  reverse=True)
    #
    #                     sents_to_keep = math.ceil(summary_sent_precent * len(sentences_dict['sentences']) / 100)
    #                     rr_selected_sent = rr_sorted_sent_list[:sents_to_keep]
    #                     rr_selected_sent = sorted(rr_selected_sent, key=lambda x: (x['chunk_id'], x['sent_id']))
    #                     selected_sent_list.extend(rr_selected_sent)
    #
    #         else:
    #             ######### take top N sentences by combining all the rhetorical roles
    #             sent_list = sorted(sent_list, key=lambda x: x['sent_score'], reverse=True)
    #             sents_to_keep = math.ceil(summary_sent_precent * len(sent_list) / 100)
    #             selected_sent_list = sent_list[:sents_to_keep]
    #             selected_sent_list = sorted(selected_sent_list, key=lambda x: (x['chunk_id'], x['sent_id']))
    #
    #         predicted_summary_rr = {}  ## keys are rhetorical role and values are concatenated sentences
    #         ## create predicted summary
    #         for sent_dict in selected_sent_list:
    #             sent_lawbriefs_role = final_categories[lawbriefs_summary_map[sent_dict['sent_rhetorical_role']]]
    #             if predicted_summary_rr.get(sent_lawbriefs_role) is None:
    #                 predicted_summary_rr[sent_lawbriefs_role] = sent_dict['sent_txt']
    #             else:
    #                 predicted_summary_rr[sent_lawbriefs_role] = predicted_summary_rr[sent_lawbriefs_role] + '\n' + \
    #                                                             sent_dict['sent_txt']
    #
    #         ######## copy the additional mandatory roles to summary
    #         if use_rhetorical_roles and add_additional_mandatory_roles_to_summary and not seperate_summary_for_each_rr:
    #             sent_list = sorted(sent_list, key=lambda x: (x['chunk_id'], x['sent_id']))
    #             for category in additional_mandatory_categories:
    #                 category_sentences = [i for i in sent_list if
    #                                       lawbriefs_summary_map[i['sent_rhetorical_role']] == category]
    #                 if category_sentences:
    #                     if predicted_summary_rr.get(category) is not None:
    #                         ###### remove the category as it may not have all the sentences.
    #                         predicted_summary_rr.pop(category)
    #                     for cat_sent in category_sentences:
    #                         if predicted_summary_rr.get(category) is None:
    #                             predicted_summary_rr[category] = cat_sent['sent_txt']
    #                         else:
    #                             predicted_summary_rr[category] = predicted_summary_rr[category] + '\n' + \
    #                                                              cat_sent['sent_txt']
    #         predicted_rr_summaries.append(predicted_summary_rr)
    #
    #     return predicted_rr_summaries

    def get_short_rhetorical_roles(sent_list,min_token_cnt_per_rr = 50):
        ####### checks if all combine sentences of a rhetorical roles are short and return list of such rhetorical roles
        rr_sents = {}  ##### keys are summary section names and values are 'token_cnt'

        #### collect all the sentenes of a summary section
        for sent_dict in sent_list:
            sent_token_cnt = len(sent_dict['sent_txt'].split())
            sent_rr = lawbriefs_summary_map[sent_dict['sent_rhetorical_role']]
            if rr_sents.get(sent_rr) is None:
                rr_sents[sent_rr] = 1
            else:
                rr_sents[sent_rr] += sent_token_cnt

        ### check which sections are short
        short_rr = []
        for rr,token_cnt in rr_sents.items():
            if token_cnt < min_token_cnt_per_rr:
                short_rr.append(rr)

        return short_rr

    def get_summary_score_threshold(sent_list):
        ####### Gives threshold for selecting summary sentences
        filtered_sent_list = [sent for sent in sent_list if re.search('[a-zA-Z]', sent['sent_txt'])]

        summary_sent_precent = get_adaptive_summary_sent_percent(len(filtered_sent_list))
        sents_to_keep = math.ceil(summary_sent_precent * len(filtered_sent_list) / 100)

        sent_scores = [i['sent_score'] for i in filtered_sent_list]
        sent_scores.sort(reverse=True)

        threshold = sent_scores[sents_to_keep+1]
        return threshold

    def get_summary_sentences(inference_output):
        ##########
        for file_name, sent_list_all in inference_output.items():
            summary_score_threshold = get_summary_score_threshold(sent_list_all) ### sentences above this threshold are included in summary
            short_rr = get_short_rhetorical_roles(sent_list_all)

            for sent in sent_list_all:
                in_summary = False
                sent_rr = lawbriefs_summary_map[sent['sent_rhetorical_role']]
                sent_summary_section = final_categories[sent_rr]
                if sent_rr in short_rr or sent_summary_section in additional_mandatory_categories or sent['sent_score']>=summary_score_threshold:
                    in_summary = True

                sent['in_summary'] = in_summary
                sent['summary_section'] = sent_summary_section

    def combine_rr_summary_outputs(summary_inference_output,rr_output):
        ###### Add the summary details to rr_output inplace
        summary_details = {} #### keys are sent_id and values are {'in_summary': True,'sent_score':0.1, 'summary_section':'ANALYSIS'}
        summary_output = list(summary_inference_output.values())[0]
        for sent in summary_output:
            in_summary_flag = sent['in_summary']
            summary_details[sent['sent_id']] = {'in_summary': in_summary_flag,
                                                'sent_score':sent['sent_score'],
                                                'summary_section':sent['summary_section']
                                                }

        ##### add the details to rr output
        for sent in rr_output[0]['result']:
            if summary_details.get(sent['value']['id']) is not None:
                sent['value'].update(summary_details[sent['value']['id']])
            else:
                if sent['value']['labels'][0] == 'PREAMBLE':
                    sent['value']['in_summary'] = True
                    sent['value']['summary_section'] = "PREAMBLE"
                else:
                    sent['value']['in_summary'] = False


    def create_summary_text(rr_output):
        sectionwise_summary = collections.defaultdict(str)
        for sent in rr_output[0]['result']:
            if sent['value']['in_summary']:
                sectionwise_summary[sent['value']['summary_section']]+= sent['value']['text'] + '\n'

        return dict(sectionwise_summary)

    get_summary_sentences(inference_output)
    combine_rr_summary_outputs(inference_output, rr_output)
    summary_texts = create_summary_text(rr_output)
    # rr_summaries = create_concatenated_summaries(inference_output)
    # rr_summaries[0]['PREAMBLE'] = preamble_text
    # summary_text = ' '.join([rr_summaries[0][key] for key in rr_summaries[0].keys()])
    # rr_summaries[0]['all_sentences_with_scores'] = _process_sentences_with_scores_and_add_percentile_ranks(
    #     inference_output, summary_text)
    return summary_texts