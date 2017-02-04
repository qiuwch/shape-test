# Generate a webpage to simulate what the iARPA challenge looks like
# So that as a human, we can imagine what challenges we are facing.

# The file organization is
# /root folder
#     /model1
#         /view1.png
#         /view2.png
#         /....
#     /model2
#         /view1.png
#         /view2.png
#         /...
#     /...

import glob, random, logging, argparse
# logging.basicConfig(level = logging.DEBUG)
logging.basicConfig(level = logging.INFO)


def main():
    # TODO: Add random seed to make sure the generated tests are the same
    parser = argparse.ArgumentParser()
    parser.add_argument('--N', default=4, type=int, help='How many candidates to choose from')
    parser.add_argument('--trials', default=1, type=int, help='How many questions to generate')
    args = parser.parse_args()

    model_folders = glob.glob("model*")
    models = [] # Models is the list
    img_ext = 'png' # Image extension to glob

    for f in model_folders:
        model = [] # Model is a list of view
        model = glob.glob(f + '/*.' + img_ext)
        models.append(model)

    logging.debug('Images of all models loaded from the disk')
    logging.debug(models) # Print debug information
    for id in range(args.trials):
        task = gen_task(models, args.N)
        task['id'] = id

        html_str = format_html(task)
        html_filename = 'trial_%d.html' % id
        with open(html_filename, 'w') as f:
            f.write(html_str)

        gt_html_str = format_html(task, highlight_gt = True)
        gt_html_filename = 'trial_%d_gt.html' % id
        with open(gt_html_filename, 'w') as f:
            f.write(gt_html_str)


def gen_task(models, num_choices):
    # Define variables
    # query_model = [] # Randomly pick a model for query
    # query_image = '' # Use this to point to the query image
    # choice_models = [[]] # Four models to choose from, including the query_model
    # choice_images = ['']

    # Random pick one model
    choice_models = random.sample(models, num_choices)
    # Sample four models, use the first as query
    query_model = choice_models[0]
    remaining_models = choice_models[1:]

    assert(len(choice_models) == num_choices)
    assert query_model in choice_models

    images_from_query = random.sample(query_model, 2)
    query_image = images_from_query[0]
    choice_images = [images_from_query[1]] \
            + [random.choice(model) for model in remaining_models]
            # Pick one image from each model
    # Make sure I did not pick the exact same image as the query_image
    assert(len(choice_images) == num_choices)

    # suffle choice images
    random.shuffle(choice_images)
    answer = choice_images.index(images_from_query[1])

    # Print debug information
    logging.debug('The query image is:')
    logging.debug(query_image)
    logging.debug('The choices are:')
    logging.debug(choice_images)

    task = {
        'query_image': query_image,
        'choice_images': choice_images,
        'answer': answer,
    }
    return task

def format_json(task):
    # return a string
    pass

def format_html(task, highlight_gt = False):

    if not highlight_gt:
        table_tpl = \
'''
<a href="trial_{next_id}.html">next</a>&nbsp;<a href="trial_{id}_gt.html">gt</a>
<table style="border: 1px;">
    <tr>{str_query_image}</tr>
    <tr>{str_test_image}</tr>
</table>
'''
    else:
        table_tpl = \
'''
<a href="trial_{next_id}.html">next</a>&nbsp;<a href="trial_{id}.html">question</a>
<table style="border: 1px;">
    <tr>{str_query_image}</tr>
    <tr>{str_test_image}</tr>
</table>
'''



    img_cell_tpl = \
'''
<td><img src='{img}' width='300px'></img></td>
'''
    gt_img_cell_tpl = \
'''
<td bgcolor="red"><img src='{img}' width='300px'></img></td>
'''
    str_query_image = img_cell_tpl.format(img=task['query_image'])
    str_test_image = ''

    choice_images = task['choice_images']
    for i in range(len(choice_images)):
        im = choice_images[i]
        if highlight_gt and (i == task['answer']):
            str_test_image += gt_img_cell_tpl.format(img = im)
        else:
            str_test_image += img_cell_tpl.format(img = im)

    # A more compact way to format str_test_image
    # str_test_image = ''.join(img_cell_tpl.format(img=im) for im in task['choice_images'])

    html_str = table_tpl.format(\
        str_query_image = str_query_image,
        str_test_image = str_test_image,
        id = task['id'],
        next_id = task['id'] + 1
    )
    return html_str

if __name__ == '__main__':
    main()
