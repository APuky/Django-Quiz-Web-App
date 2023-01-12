def get_average(category, scores, model):
    cat = scores.filter(quiz__category=str(category))
    score_list = []
    for quiz in cat:
        num_of_questions = model.objects.filter(quiz=quiz.quiz).count()
        user_score = quiz.points
        avg_score = user_score / num_of_questions
        score_list.append(avg_score)

    if not score_list:
        ## Ako nema niti jedan riješen kviz u kategoriji
        return 0
    else:
        scores_avg = round(sum(score_list) / len(score_list) * 100, 1)
        if scores_avg.is_integer():
            return int(scores_avg)
        return scores_avg


def get_amount_of_solved(category, scores, model):
    ##https://stackoverflow.com/questions/3852104/select-distinct-individual-columns-in-django
    quizes_solved = scores.filter(quiz__category=str(category)).values('quiz').distinct().count()
    num_of_quizes = model.objects.filter(category=str(category)).count()
    if num_of_quizes == 0:
        return 0
    solved = round ((quizes_solved / num_of_quizes) * 100, 1)
    if solved.is_integer():
        return int(solved)
    return solved