from requests import get

from .utils import NotFoundError


class Client:
    base_cache = {}
    change_cache = {}

    @classmethod
    def get_base(cls, post_id):
        if post_id not in cls.base_cache.keys():
            res = get(f'http://lgulife.furchain.xyz/base?post_id={post_id}')
            if res.status_code == 200:
                result = res.json()
                result['post_id'] = result.pop('_id')
                cls.base_cache[post_id] = result
                return cls.base_cache[post_id].copy()
            elif res.status_code == 404:
                raise NotFoundError(f'post {post_id}')
            else:
                raise Exception(res.text, res.status_code)
        return cls.base_cache[post_id]

    @classmethod
    def get_change_after(cls, post_id, start):
        res = get(f'http://lgulife.furchain.xyz/change?post_id={post_id}&start={start}')
        if res.status_code != 200:
            raise Exception(res.text, res.status_code)
        return res.json()

    @classmethod
    def get_change(cls, post_id):
        if post_id in cls.change_cache.keys():
            result = cls.get_change_after(post_id, cls.change_cache[post_id]['version'][-1])
        else:
            cls.change_cache[post_id] = {'version':[],'post':[],'comment':[]}
            result = cls.get_change_after(post_id, '')
        cls.change_cache[post_id]['version'].extend(result['version'])
        cls.change_cache[post_id]['post'].extend(result['post'])
        cls.change_cache[post_id]['comment'].extend(result['comment'])
        return cls.change_cache[post_id].copy()
