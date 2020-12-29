from flask import Flask, render_template, request, render_template_string, redirect, url_for
import db
from prod_options import *
from bson.objectid import ObjectId
from google.cloud import storage
from io import BytesIO
from PIL import Image
import mimetypes
import io 
from os import environ, remove, path, makedirs
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# creates a Flask application, named app
app = Flask(__name__, template_folder='templates')


@app.route("/")
def home():


    # fetch the _id of product and name of product.

    data = db.collection.find({})

    opt_insert = request.args.get("inserted")
    opt_remove = request.args.get("removed")
    opt_update = request.args.get("updated")
    
    return render_template('index.html', Category = Category, 
                                        Brand= Brand,
                                        Finish= Finish,
                                        Hold= Hold,
                                        HairType= HairType,
                                        curr_data = data,
                                        db_options = db_options,
                                        inserted= opt_insert,
                                        removed= opt_remove,
                                        updated= opt_update
                            )



@app.route('/insertProduct', methods = ['POST'])
def insertProduct():

    name = request.form['name'] 
    categ = int(request.form['categ'])
    brand = int(request.form['brand'])
    finish= int(request.form['finish'])
    hold = int(request.form['hold'])
    type= request.form.getlist('hairtype')
    smell = request.form['smell']
    desc = request.form['desc']
    img = request.files['img']

    get_url = getUploadedURL(img)

    insert_data = {"category": categ, 'brand' : brand, 'name': name , 'hold' : hold, 'finish' : 
    finish, 'hair' : elementsToInt(type), 'fragrance': smell, 'description': desc, "image": get_url.generateImg(), 'webp_image': get_url.generateWebp()}
    db.collection.insert_one(insert_data)

    print(img)
    return redirect(url_for('.home', inserted=True))



@app.route('/updateProduct', methods= ['POST'])
def updateProduct():

    opt = request.form.getlist('upd_options')
    id = request.form['idUpdate']
    # for i in range(0, len(opt) + 1):
    #     opt[i] = db_options[int(opt[i]) + 1]
    
    for i in range(0, len(opt)):

    # generalise the variables here 
    # name, desc and frag are character based
    # brand, hold, finish, category are digit based
    # image is fileStorage
    # hair is array
       
        
        if opt[i] == "name" or opt[i] == "description" or opt[i] == "fragrance":
            val = request.form[opt[i]] 
            db.collection.update_one({'_id':ObjectId(id)}, {'$set': {opt[i]: val}}, upsert=False)

        elif opt[i] == "hair":
            type= request.form.getlist('hair')

            db.collection.update_one({'_id':ObjectId(id)}, {'$set': {'hair': elementsToInt(type)}}, upsert=False)

        elif opt[i] == "image":

            img = request.files['image']

            get_url = getUploadedURL(img)

            db.collection.update_one({'_id':ObjectId(id)}, {'$set': {'image': get_url.generateImg(), 'webp_image': get_url.generateWebp()}}, upsert=False)
        else:
            val = int(request.form[opt[i]])
            db.collection.update_one({'_id':ObjectId(id)}, {'$set': {opt[i]: val}}, upsert=False)


    return redirect(url_for('.home', updated=True))


@app.route('/removeProduct', methods = ['POST'])
def removeProduct():

    id = request.form['idRemove']
    removeData = {"_id": ObjectId(id)}
    db.collection.delete_one(removeData)

    return redirect(url_for('.home', removed=True))


class getUploadedURL:
    def __init__(self, imageFile):

        self.bucket = storage.Client().get_bucket(environ.get('CLOUD_STORAGE_BUCKET'))
        self.imgFile = imageFile
        self.filename, self.file_ext = path.splitext(self.imgFile.filename)
        self.pic = Image.open(BytesIO(self.imgFile.read()))
        self.final_folder = './compressed-images-bucket/'
        

    def generateImg(self):

        # file_ext = mimetypes.guess_extension(imgFile.content_type)
        if not path.exists(self.final_folder):
            makedirs(self.final_folder)

        if self.file_ext == ".png":
            self.pic.convert(mode='P', palette=Image.ADAPTIVE).save(self.final_folder + self.imgFile.filename, optimize=True, quality=40)
        else: 
            self.pic.save(self.final_folder + self.imgFile.filename, 'JPEG', quality=40, optimize=True)

        # pic.save(final_folder + self.filename + '.webp', 'webp')

        # print(self.imgFile.filename)
        blob = self.bucket.blob(self.imgFile.filename)
        blob.upload_from_filename(self.final_folder + self.imgFile.filename)

        #remove(self.final_folder + self.imgFile.filename)

        return blob.public_url

    def generateWebp(self):

        self.pic.save(self.final_folder + self.filename + '.webp', 'webp')

        blobWebp = self.bucket.blob(self.filename + '.webp')

        blobWebp.upload_from_filename(self.final_folder + self.filename + '.webp')

        return blobWebp.public_url


def elementsToInt(type):
    type = [ int(x) for x in type]
    return type

# run the application
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=3001)