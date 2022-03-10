## Project - Deliverable \# 2 Feedback 

How can we test the accuracy of our model to predict development/decay?

There are different strategies like Root mean squared error. Here are some links that can help with this: 

https://datascience.stackexchange.com/questions/36083/predict-the-accuracy-of-linear-regression 

https://towardsdatascience.com/what-are-the-best-metrics-to-evaluate-your-regression-model-418ca481755b 

- Could you recommend specific packages to run a regression model?

I think the best package to use is SKLearn package. It will have everything that you will need. 

- Our most pressing concern is how to handle interactivity. Initially we considered giving
users the ability to select their own regressors, but we have agreed to set that aside.
Instead, we are considering allow users to specify a community area to get more
information about. And perhaps run a sub-regression between building permits and crime
within that community area, to see how the regression coefficients shift across the city as
a whole.

Yes, it's limited interactivity then what I would expect but at this point it's important to have some type of interactivity. You could always look into Python Dash. It's easier to get something going using that tool and will help build up the interactivity component. 

*Grade*: 10/10 
