import docker, socket
from re import sub
import os


def p(s):
    print(s)


def d(s):
    dir(s)


def h(s):
    help(s)


class ImageServer(object):
    def __init__(self):
        super(ImageServer, self).__init__()
        self.servers = []
        self.images = []
        self.remote_images = dict()
        self.client = docker.from_env()
        # self.parse_images_id(self.client.images.list())
        self.quest_for_servers()

    def have_i_image(self, id):
        return id in self.images

    def quest_for_servers(self):
        # if os.getenv("SERVERS"):
        self.servers = (os.getenv("ShR_SERVERS")).split(' ')
        return
        # from netaddr import IPNetwork
        # ip = IPNetwork('127.0.0.0/24')
        # for addr in ip:
        #     server = str(addr)
        #     try:
        #         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #         result = sock.connect_ex((server, 4243))
        #         if result == 0:
        #             docker.DockerClient(base_url='http://{}:{}'.format(server, 4243))
        #             self.servers.append(server)
        #     except:
        #         pass
        #     sock.close()

    def parse_images_id(self, imagelist):
        for image in imagelist:
            self.images.append(image.id)

    def look_for_image_local(self, image):
        try:
            img = self.client.images.get(image)
            return True
        except Exception:
            return False

    def look_for_image_remote(self, image):
        available_on = []
        for server in self.servers:
            try:
                client = docker.DockerClient(base_url=self.construct_address(server))

                image_1 = client.images.get(image)
                available_on.append(server)
            except Exception as e:
                # print(e)
                pass

        if len(available_on) == 0:
            raise Exception("No such image on any of servers")
        self.remote_images[image_1.id] = available_on
        for tag in image_1.tags:
            self.remote_images[tag] = available_on
            if ":latest" in tag:
                self.remote_images[tag.split(':')[0]] = available_on
        return available_on[0]

    def construct_address(self, server=None):
        if server:
            return 'http://{}:{}'.format(server, 4243)
        servers = []
        for index in range(len(self.servers) - 1):
            if "http" in self.servers[index] and "4243" in self.servers[index]:
                pass
            self.servers[index] = f'http://{self.servers[index]}:4243'.format(self.servers[index], 4243)

    def new_client(self, address=None):
        if address:
            return docker.DockerClient(base_url=self.construct_address(address))
        return docker.from_env()

    def clean_image_string(self, image_string):
        return sub("[^\d\w]", "", image_string)

    def get_image_from_remote(self, image, server=None, save=True):
        if not server:
            server = self.look_for_image_remote(image)
        client = self.new_client(server)
        image_object = client.images.get(image)
        if save:
            with open(self.clean_image_string(image) + ".tar", 'wb') as w:
                for i in image_object:
                    w.write(i)
        else:
            return image_object
    def tag_image(self,image, tags):
        for tag in tags:
            self.client.images.get(image).tag(tag)


    def import_image(self, image_object):
        self.client.images.load(image_object.save())
        self.tag_image(image_object.id, image_object.tags)


if __name__ == "__main__":
    a = ImageServer()
    a.import_image(a.get_image_from_remote(os.getenv('ShR_IMAGE'), save=False))
