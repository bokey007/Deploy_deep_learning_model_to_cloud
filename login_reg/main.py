from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
#from werkzeug.utils import secure_filename
#import os
from . import app
#from . import db

main = Blueprint('main', __name__)
out_class = None
out_score = None


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


def allowed_image(filename):

    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

def process_image(im):
    from torchvision import models
    import torch

    global out_class
    global out_score

    dir(models)

    alexnet = models.alexnet(pretrained=True)

    from torchvision import transforms
    transform = transforms.Compose([  # [1]
        transforms.Resize(256),  # [2]
        transforms.CenterCrop(224),  # [3]
        transforms.ToTensor(),  # [4]
        transforms.Normalize(  # [5]
            mean=[0.485, 0.456, 0.406],  # [6]
            std=[0.229, 0.224, 0.225]  # [7]
        )])

    # Import Pillow
    from PIL import Image
    img = Image.open(im)

    img_t = transform(img)
    batch_t = torch.unsqueeze(img_t, 0)

    alexnet.eval()

    out = alexnet(batch_t)
    img.close()
    print(out.shape)

    with open('imagenet_classes.txt') as f:
        classes = [line.strip() for line in f.readlines()]

    _, index = torch.max(out, 1)

    percentage = torch.nn.functional.softmax(out, dim=1)[0] * 100
    out_class = classes[index[0]]
    out_score = percentage[index[0]].item()

    return out_class, out_score

@main.route('/profile', methods=["GET", "POST"])
@login_required
def upload_image():

    if request.method == "POST":

        disclaimer = True if request.form.get('Disclaimer') else False

        if disclaimer:

            if request.files:

                image = request.files["image"]
                print(type(image))

                if image.filename == "":
                    print("No filename")
                    del image
                    return redirect(request.url)

                if allowed_image(image.filename):
                    #filename = secure_filename(image.filename)

                    #image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                    #process image
                    process_image(image)
                    ot_cls = str(out_class)
                    ot_score = str(out_score)
                    msg1 = "Class is "
                    msg2 = " with score of "
                    msg_f = msg1 + ot_cls + msg2 + ot_score
                    #flash the score
                    flash(msg_f)
                    del image
                    return redirect(url_for('main.profile'))
                    print("Image saved")

                else:
                    print("That file extension is not allowed")
                    del image
                    return redirect(request.url)
        else:
            flash('Please accept the Disclaimer by clicking against the checkbox and then '
                  'select and upload the file again')



    return redirect(url_for('main.profile'))