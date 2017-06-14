Censored
========

## What to do?

Cost: 0%

Your task here is to get a program which you can edit **pdf** files with, open the document with it and move the censored picture.

## Looking for the right tool

Cost: 20%

While looking at the document, it's easy to notice that you won't be able to restore the key, if you handle the document's parts together.
Look at the extension, it's **pdf**... Maybe you should take a look at **LibreOffice**?

## Finding the right tool

Cost: 20%

If you take a look at **LibreOffice** tools, you can find out soon, that **LibreOffice Draw** is the right tool for you. You can edit **pdf** files with it.
As mentioned earlier, there are more parts of the document...

## Moving one part of the document

Cost: 50%

If you open the document with **LibreOffice Draw**, you can drag and move the picture with the `Censored` text on it. Move your cursor over it,
click and hold the left mouse button, and then move the picture from above the other picture.

## Complete solution

To get the flag, you need to download **LibreOffice**. There's a program named **LibreOffice Draw** in it. You should open the downloaded document with **LibreOffice Draw**. Move your cursor above the picture with the `Censored` text on it, click and hold it with the left mouse button, move it down for example to be able to see the whole picture with the flag on it. It's another picture, so you have to write the whole flag down, you can't copy and paste it.

There are some more ways to get the flag: one is to use pdf forensics tools. You can find more information about this at this [page](http://theevilbit.blogspot.hu/2014_10_01_archive.html).

Other way is to use any text editor program, for example **notepad++**. Open the pdf with that and look at it a little bit. You can see that there are objects in the file(`2 0 obj ... endobj`). Delete one object and try to open the document. If you deleted an object you shouldn't have, undo every modifications and delete another object.
`5 0 obj` will be what you're looking for...

Writeup credits: Dávid Gyulánszki (gyulanszki.david@gmail.com)
