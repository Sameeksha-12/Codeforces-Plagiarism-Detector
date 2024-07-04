from django.shortcuts import render,get_object_or_404,redirect
from .models import Contest, User, Submission
from .utils import fetch_top_users,fetch_submission_code,check_code_similarity
# Create your views here.

def home(request):
    if request.method == "POST":
        contest_id = request.POST.get('contest_id')
        return redirect('contest_leaderboard',contest_id=contest_id)
    return render(request, 'submissions/home.html')

def contest_leaderboard(request,contest_id):
    try:
        contest = Contest.objects.get(contest_id=contest_id)
        if not contest.fetched:
            fetch_top_users(contest_id)
            contest = Contest.objects.get(contest_id=contest_id)
        users = User.objects.filter(contest=contest).order_by('rank')
        return render(request, 'submissions/contest_leaderboard.html', {'contest':contest, 'users': users})
    except Contest.DoesNotExist:
        fetch_top_users(contest_id)
        contest = Contest.objects.get(contest_id=contest_id)
        users = User.objects.filter(contest=contest).order_by('rank')
        return render(request, 'submissions/contest_leaderboard.html',{'contest':contest, 'users':users})


def user_submissions(request, contest_id, user_id):
    user = get_object_or_404(User, id=user_id)
    submissions = Submission.objects.filter(user=user, contest__contest_id=contest_id)
    return render(request, 'submissions/user_submissions.html', {'user': user, 'submissions': submissions})

def check_similarity(request,contest_id):
    contest = get_object_or_404(Contest,contest_id=contest_id)
    users = User.objects.filter(contest=contest)

    for user in users:
        submissions = Submission.objects.filter(user=user,contest=contest,fetched=False,verdict='OK')
        for submission in submissions:
            fetch_submission_code(submission)

    similarity_results = check_code_similarity(contest)

    return render(request, 'submissions/similarity_results.html', {'contest':contest,'results':similarity_results})