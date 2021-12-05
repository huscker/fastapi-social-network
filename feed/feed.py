def update_post_data(posts: list):
    '''
    Prepare raw post data and convert it to more JSON ish format
    :param posts
    :return: list()
    '''
    posts = list(map(lambda x: list(x), posts))
    for i in range(len(posts)):
        posts[i] = {
            'id': posts[i][1],
            'title': posts[i][3],
            'description': posts[i][4],
            'liked': posts[i][5],
            'owner': posts[i][0],
            'owner_id': posts[i][2],
            'image_src': update_file_path(posts[i][1])
        }
    return posts


def update_file_path(fname: str):
    '''
    Get file path from id
    :param fname: id of file
    :return: string()
    '''
    return f'/static/{fname}.png'
