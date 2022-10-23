import os
import shutil

my_path = '/'.join(os.path.abspath(__file__).replace('\\', '/').split('/')[:-1])
out_path = 'data_yolo'

class CSVDataReader:
    def __init__(self, filename):
        self.__file = open(filename)
        self.__tagindex = {}
        self.__tagtype = {}
        tagline = self.__file.readline().strip()
        for i,tag in enumerate(tagline.split(',')):
            self.__tagindex[tag.lower()] = i
            self.__tagtype[tag.lower()] = str

    def settype(self, key, datatype):
        self.__tagtype[key] = datatype

    def getline(self):
        linestr = self.__file.readline().strip()
        if not linestr:
            return {}
        dataline = linestr.split(',')
        result = {}
        for k in self.__tagindex:
            result[k] = self.__tagtype[k](dataline[self.__tagindex[k]])
        return result

    def close(self):
        self.__file.close()


class YoloConverter:
    def __init__(self, outputdir):
        self.classlist = {}
        self.outdir = outputdir

    def addclass(self, classname, asid):
        self.classlist[classname] = asid

    def convert(self):
        self.convertcsvs()
        self.makeimgdata()
        
        f = open(f'{self.outdir}/data.yaml', 'w')
        f.write(f'train: {my_path}/{self.outdir}/dataSet/train.txt\n')
        f.write(f'test: {my_path}/{self.outdir}/dataSet/test.txt\n')
        f.write(f'val: {my_path}/{self.outdir}/dataSet/val.txt\n')
        f.write(f'nc: {len(self.classlist)}\n')
        f.write(f'names: {list(self.classlist.keys())}\n')
        f.close()

    def makeimgdata(self):
        print('Collecting image data...', end='')
        os.mkdir(f'{self.outdir}/dataSet')
        os.mkdir(f'{self.outdir}/images')

        shutil.copytree('test', f'{self.outdir}/images/test')
        shutil.copytree('train', f'{self.outdir}/images/train')
        shutil.copytree('validation', f'{self.outdir}/images/val')

        imgid_test = [p.replace('.jpg', '') for p in os.listdir(f'{self.outdir}/images/test')]
        imgid_train = [p.replace('.jpg', '') for p in os.listdir(f'{self.outdir}/images/train')]
        imgid_val = [p.replace('.jpg', '') for p in os.listdir(f'{self.outdir}/images/val')]

        f = open(f'{self.outdir}/dataSet/test.txt', 'w')
        for imageid in imgid_test:
            f.write(os.path.abspath(f'{self.outdir}/images/test/{imageid}.jpg')+'\n')
        f.close()

        f = open(f'{self.outdir}/dataSet/train.txt', 'w')
        for imageid in imgid_train:
            f.write(os.path.abspath(f'{self.outdir}/images/train/{imageid}.jpg')+'\n')
        f.close()

        f = open(f'{self.outdir}/dataSet/val.txt', 'w')
        for imageid in imgid_val:
            f.write(os.path.abspath(f'{self.outdir}/images/val/{imageid}.jpg')+'\n')
        f.close()

        print('Done')

    def convertcsvs(self):
        os.mkdir(f'{self.outdir}/labels')
        os.mkdir(f'{self.outdir}/labels/test')
        os.mkdir(f'{self.outdir}/labels/train')
        os.mkdir(f'{self.outdir}/labels/val')
        self.convertonecsv('sub-test-annotations-bbox.csv', f'{self.outdir}/labels/test')
        self.convertonecsv('sub-train-annotations-bbox.csv', f'{self.outdir}/labels/train')
        self.convertonecsv('sub-validation-annotations-bbox.csv', f'{self.outdir}/labels/val')

    def convertonecsv(self, filename, outputdir):
        print(f'Converting "{filename}"...', end='')
        csv = CSVDataReader(filename)
        csv.settype('xmin', float)
        csv.settype('xmax', float)
        csv.settype('ymin', float)
        csv.settype('ymax', float)

        while True:
            csvline = csv.getline()
            if not csvline:
                break

            filename = f'{outputdir}/{csvline["imageid"]}.txt'
            if os.path.exists(filename):
                f = open(filename, 'a')
            else:
                f = open(filename, 'w')

            tag = self.classlist[csvline['classname']]
            xc = (csvline['xmin'] + csvline['xmax'])/2
            yc = (csvline['ymin'] + csvline['ymax'])/2
            w = csvline['xmax'] - csvline['xmin']
            h = csvline['ymax'] - csvline['ymin']
            f.write(f'{tag} {xc} {yc} {w} {h}\n')
            f.close()

        csv.close()
        print('Done')


if __name__ == '__main__':

    try:
        os.mkdir(out_path)
    except FileExistsError:
        print(f'"{out_path}" exists!')
        raise

    yolo = YoloConverter(out_path)
    yolo.addclass('Tomato', 1)
    yolo.addclass('Bell pepper', 0)
    yolo.convert()
    

