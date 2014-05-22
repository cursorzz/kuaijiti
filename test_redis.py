#-*- coding:utf-8 -*-
 
def test_redis():
    ### 开发者在requirements.txt中指定依赖redis使用
    import redis
    ### 请在管理控制台获取host, port, db_name, api_key, secret_key的值 
    db_name = "xpmunVCjmcXwbGgzPXRO"
    api_key = "aBv5vhN9Lggo58zURGFsHE56"
    secret_key = "FOnYOKWYnT92fT7VMcVWUfY6MGMfm1Su"
    myauth = "%s-%s-%s"%(api_key, secret_key, db_name)
 
    ### 连接redis服务
    r = redis.Redis(host = "redis.duapp.com", port = 80, password = myauth)
 
    ### 进行各种redis操作，如set、get
    r.set("foo", "bar")
    return "get foo=> %s success!"%r.get("foo")
 
 
def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html')]
    start_response(status, headers)
    try:
        return test_redis()
    except:
        return 'handle exception'
 
from bae.core.wsgi import WSGIApplication
application = WSGIApplication(app)
