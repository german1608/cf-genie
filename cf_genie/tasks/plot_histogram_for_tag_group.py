import cf_genie.logger as logger
import cf_genie.utils as utils

import matplotlib.pyplot as plt

logger.setup_applevel_logger(
    is_debug=False, file_name=__file__, simple_logs=True)


log = logger.get_logger(__name__)

COLORS = ['red', 'green', 'blue', 'cyan', 'yellow', 'magenta']

def main():
    log.info('Generating histogram')

    df = utils.read_cleaned_dataset()

    df_grouped_by_tag_group = df.groupby(['most_occurrent_tag_group'])['most_occurrent_tag_group'].count()

    log.info('Dataframe aggegated by most_occurrent_tag_group')
    log.info(df_grouped_by_tag_group.head())
    
    plt.figure(figsize=(8, 5))
    plt.bar(df_grouped_by_tag_group.index, df_grouped_by_tag_group.values, color=COLORS)
    plt.ylabel('Number of Occurrences', fontsize=12)
    plt.xlabel('Product', fontsize=12)
    plt.title('Number of problems per tag group', fontsize=16)
    # plt.show()

    utils.write_plot('histogram_all_tag_groups.png', plt)

    df_grouped_by_tag_group = df_grouped_by_tag_group[df_grouped_by_tag_group.index != 'ADHOC']
    log.info('Removing ADHOC out of the equation')
    log.info(df_grouped_by_tag_group.head())

    plt.figure(figsize=(8, 5))
    plt.bar(df_grouped_by_tag_group.index, df_grouped_by_tag_group.values, color=COLORS[1:])
    plt.ylabel('Number of Occurrences', fontsize=12)
    plt.xlabel('Product', fontsize=12)
    plt.title('Number of problems per tag group (without ADHOC)', fontsize=16)
    # plt.show()

    utils.write_plot('histogram_without_adhoc_tag_groups.png', plt)


if __name__ == '__main__':
    main()
